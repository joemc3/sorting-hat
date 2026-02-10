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

  return (
    <div className="space-y-0.5">
      {rootNodes.map((node) => (
        <TreeNode
          key={node.id}
          node={node}
          childrenMap={childrenMap}
          selectedId={selectedId}
          onSelect={onSelect}
          defaultExpanded={isSearching ? true : node.level <= 2}
        />
      ))}
    </div>
  );
}
