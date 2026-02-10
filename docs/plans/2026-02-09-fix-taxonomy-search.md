# Fix Taxonomy Search Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix taxonomy search so matching nodes are always visible in the tree and results are ranked by relevance.

**Architecture:** Two changes work together: (1) backend `search_nodes` includes ancestor nodes in results so the tree hierarchy is always complete, and (2) frontend tree auto-expands all nodes during search so matches aren't hidden behind collapsed parents. Additionally, name matches are ranked above definition/characteristic substring matches.

**Tech Stack:** Python/SQLAlchemy (backend), TypeScript/React (frontend)

---

## Root Cause

The search API returns a flat list of nodes where name/definition/characteristics contain the query substring. The tree component rebuilds hierarchy from `parent_id` — nodes whose parent isn't in the result set become orphaned and invisible. Example: searching "IDE" matches "IDEs & Code Editors" but its parent "Application Development & Platform" doesn't match, so "IDEs & Code Editors" never renders.

---

### Task 1: Backend — Include ancestor nodes in search results

**Files:**
- Modify: `api/src/sorting_hat/services/taxonomy.py:184-196`
- Test: `api/tests/test_taxonomy_service.py`

**Step 1: Write failing test**

Add to `api/tests/test_taxonomy_service.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from sorting_hat.services.taxonomy import TaxonomyService


@pytest.mark.asyncio
async def test_search_nodes_includes_ancestors():
    """search_nodes should include ancestor nodes so the tree renders correctly."""
    # Create mock nodes: grandparent -> parent -> child (the match)
    grandparent = MagicMock()
    grandparent.id = "gp-id"
    grandparent.parent_id = None
    grandparent.name = "Software"

    parent = MagicMock()
    parent.id = "p-id"
    parent.parent_id = "gp-id"
    parent.name = "App Dev"

    child = MagicMock()
    child.id = "c-id"
    child.parent_id = "p-id"
    child.name = "IDEs & Code Editors"

    # Mock session: first call returns the search match, second returns ancestors
    session = AsyncMock()
    # search query returns only the child
    search_result = MagicMock()
    search_result.scalars.return_value.all.return_value = [child]
    # ancestor queries return parent, then grandparent
    parent_result = MagicMock()
    parent_result.scalar_one_or_none.return_value = parent
    grandparent_result = MagicMock()
    grandparent_result.scalar_one_or_none.return_value = grandparent
    root_result = MagicMock()
    root_result.scalar_one_or_none.return_value = None

    session.execute.side_effect = [search_result, parent_result, grandparent_result, root_result]

    service = TaxonomyService(session)
    results = await service.search_nodes("IDE")

    ids = [n.id for n in results]
    assert "c-id" in ids, "Matching child node should be in results"
    assert "p-id" in ids, "Parent ancestor should be in results"
    assert "gp-id" in ids, "Grandparent ancestor should be in results"
```

**Step 2: Run test to verify it fails**

Run: `cd api && .venv/bin/python -m pytest tests/test_taxonomy_service.py::test_search_nodes_includes_ancestors -v`
Expected: FAIL — current `search_nodes` doesn't fetch ancestors

**Step 3: Implement the fix**

In `api/src/sorting_hat/services/taxonomy.py`, replace the `search_nodes` method (lines 184-196):

```python
async def search_nodes(self, query: str) -> list[TaxonomyNode]:
    pattern = f"%{query}%"
    result = await self.session.execute(
        select(TaxonomyNode)
        .where(
            TaxonomyNode.name.ilike(pattern)
            | TaxonomyNode.definition.ilike(pattern)
            | TaxonomyNode.distinguishing_characteristics.ilike(pattern)
        )
        .order_by(TaxonomyNode.path)
        .limit(50)
    )
    matches = list(result.scalars().all())

    # Collect all ancestor IDs needed to build complete tree paths
    seen_ids = {n.id for n in matches}
    missing_parent_ids = {
        n.parent_id for n in matches if n.parent_id and n.parent_id not in seen_ids
    }

    ancestors: list[TaxonomyNode] = []
    while missing_parent_ids:
        result = await self.session.execute(
            select(TaxonomyNode).where(TaxonomyNode.id.in_(missing_parent_ids))
        )
        batch = list(result.scalars().all())
        if not batch:
            break
        ancestors.extend(batch)
        seen_ids.update(n.id for n in batch)
        missing_parent_ids = {
            n.parent_id for n in batch if n.parent_id and n.parent_id not in seen_ids
        }

    # Return ancestors first (sorted by path), then matches (sorted by path)
    ancestors.sort(key=lambda n: n.path)
    return ancestors + matches
```

**Step 4: Run test to verify it passes**

Run: `cd api && .venv/bin/python -m pytest tests/test_taxonomy_service.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add api/src/sorting_hat/services/taxonomy.py api/tests/test_taxonomy_service.py
git commit -m "fix: include ancestor nodes in search results for complete tree rendering"
```

---

### Task 2: Frontend — Auto-expand all tree nodes during search

**Files:**
- Modify: `web/src/components/taxonomy-tree.tsx:15`
- Modify: `web/src/app/taxonomy/page.tsx:63`

**Step 1: Add `isSearching` prop to TaxonomyTree and TreeNode**

In `web/src/components/taxonomy-tree.tsx`, update the component to accept and pass through an `isSearching` prop. When `isSearching` is true, TreeNode defaults to expanded:

```typescript
// taxonomy-tree.tsx — full replacement

"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import type { TaxonomyNode } from "@/lib/api";

interface TreeNodeProps {
  node: TaxonomyNode;
  childrenMap: Map<string | null, TaxonomyNode[]>;
  selectedId: string | null;
  onSelect: (node: TaxonomyNode) => void;
  defaultExpanded: boolean;
}

function TreeNode({ node, childrenMap, selectedId, onSelect, defaultExpanded }: TreeNodeProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const children = childrenMap.get(node.id) || [];
  const hasChildren = children.length > 0;

  return (
    <div>
      <button
        onClick={() => {
          onSelect(node);
          if (hasChildren) setExpanded(!expanded);
        }}
        className={cn(
          "flex items-center gap-1 w-full text-left px-2 py-1 rounded text-sm hover:bg-muted transition-colors",
          selectedId === node.id && "bg-primary/10 text-primary font-medium"
        )}
        style={{ paddingLeft: `${(node.level - 1) * 16 + 8}px` }}
      >
        {hasChildren && (
          <span className="w-4 text-xs text-muted-foreground">
            {expanded ? "\u25BC" : "\u25B6"}
          </span>
        )}
        {!hasChildren && <span className="w-4" />}
        <span>{node.name}</span>
      </button>
      {expanded &&
        children.map((child) => (
          <TreeNode
            key={child.id}
            node={child}
            childrenMap={childrenMap}
            selectedId={selectedId}
            onSelect={onSelect}
            defaultExpanded={defaultExpanded}
          />
        ))}
    </div>
  );
}

interface TaxonomyTreeProps {
  nodes: TaxonomyNode[];
  selectedId: string | null;
  onSelect: (node: TaxonomyNode) => void;
  isSearching?: boolean;
}

export function TaxonomyTree({ nodes, selectedId, onSelect, isSearching = false }: TaxonomyTreeProps) {
  const childrenMap = new Map<string | null, TaxonomyNode[]>();
  for (const node of nodes) {
    const parentId = node.parent_id;
    if (!childrenMap.has(parentId)) childrenMap.set(parentId, []);
    childrenMap.get(parentId)!.push(node);
  }

  const rootNodes = childrenMap.get(null) || [];
  const defaultExpanded = isSearching || false;

  return (
    <div className="space-y-0.5">
      {rootNodes.map((node) => (
        <TreeNode
          key={node.id}
          node={node}
          childrenMap={childrenMap}
          selectedId={selectedId}
          onSelect={onSelect}
          defaultExpanded={defaultExpanded ? true : node.level <= 2}
        />
      ))}
    </div>
  );
}
```

**Step 2: Pass `isSearching` from taxonomy page**

In `web/src/app/taxonomy/page.tsx`, update the TaxonomyTree usage (around line 63):

```tsx
<TaxonomyTree
  nodes={nodes}
  selectedId={selectedNode?.id ?? null}
  onSelect={handleSelect}
  isSearching={search.length > 0}
/>
```

**Step 3: Type-check**

Run: `cd web && npx tsc --noEmit`
Expected: No errors

**Step 4: Commit**

```bash
git add web/src/components/taxonomy-tree.tsx web/src/app/taxonomy/page.tsx
git commit -m "fix: auto-expand all tree nodes when searching taxonomy"
```

---

### Task 3: Backend — Debounce-friendly search by requiring min 2 chars

**Files:**
- Modify: `api/src/sorting_hat/routes/taxonomy.py:100`

**Step 1: Increase `min_length` from 1 to 2**

In `api/src/sorting_hat/routes/taxonomy.py`, line 100, change:

```python
q: str = Query(..., min_length=2, description="Text to search for in node names and definitions"),
```

This prevents single-character searches that return nearly everything.

**Step 2: Run existing tests**

Run: `cd api && .venv/bin/python -m pytest tests/ -v`
Expected: ALL PASS

**Step 3: Commit**

```bash
git add api/src/sorting_hat/routes/taxonomy.py
git commit -m "fix: require min 2 chars for taxonomy search to reduce noise"
```

---

### Task 4: Rebuild and verify in browser

**Step 1: Rebuild Docker containers**

```bash
docker compose build --no-cache api web && docker compose up -d api web
```

**Step 2: Verify in browser**

- Navigate to the taxonomy page
- Type "IDE" in the search box
- Verify "IDEs & Code Editors" appears in the tree under "Application Development & Platform"
- Verify the tree is fully expanded showing all matches
- Verify irrelevant matches are reduced
- Hard-refresh browser if needed (Cmd+Shift+R) due to Next.js cache

**Step 3: Final commit if any adjustments needed**
