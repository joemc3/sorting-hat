import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sorting_hat.models.taxonomy import Branch, GovernanceGroup, TaxonomyNode
from sorting_hat.schemas.taxonomy import (
    GovernanceGroupCreate,
    GovernanceGroupUpdate,
    TaxonomyNodeCreate,
    TaxonomyNodeUpdate,
)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


class TaxonomyServiceError(Exception):
    pass


class TaxonomyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # --- Governance Groups ---

    async def list_governance_groups(self) -> list[GovernanceGroup]:
        result = await self.session.execute(
            select(GovernanceGroup).order_by(GovernanceGroup.sort_order)
        )
        return list(result.scalars().all())

    async def get_governance_group(self, slug: str) -> GovernanceGroup | None:
        result = await self.session.execute(
            select(GovernanceGroup).where(GovernanceGroup.slug == slug)
        )
        return result.scalar_one_or_none()

    async def create_governance_group(self, data: GovernanceGroupCreate) -> GovernanceGroup:
        group = GovernanceGroup(**data.model_dump())
        self.session.add(group)
        await self.session.flush()
        return group

    async def update_governance_group(
        self, slug: str, data: GovernanceGroupUpdate
    ) -> GovernanceGroup | None:
        group = await self.get_governance_group(slug)
        if not group:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(group, field, value)
        await self.session.flush()
        return group

    async def delete_governance_group(self, slug: str) -> bool:
        group = await self.get_governance_group(slug)
        if not group:
            return False
        # Check for nodes
        result = await self.session.execute(
            select(TaxonomyNode).where(TaxonomyNode.governance_group_id == group.id).limit(1)
        )
        if result.scalar_one_or_none():
            raise TaxonomyServiceError("Cannot delete group with existing nodes")
        await self.session.delete(group)
        await self.session.flush()
        return True

    # --- Taxonomy Nodes ---

    async def get_node(self, node_id: str) -> TaxonomyNode | None:
        result = await self.session.execute(
            select(TaxonomyNode)
            .where(TaxonomyNode.id == node_id)
            .options(selectinload(TaxonomyNode.children))
        )
        return result.scalar_one_or_none()

    async def list_nodes(
        self,
        branch: str | None = None,
        governance_group_slug: str | None = None,
        max_depth: int | None = None,
    ) -> list[TaxonomyNode]:
        query = select(TaxonomyNode).order_by(TaxonomyNode.path, TaxonomyNode.sort_order)
        if branch:
            query = query.where(TaxonomyNode.branch == branch)
        if governance_group_slug:
            query = query.join(GovernanceGroup).where(GovernanceGroup.slug == governance_group_slug)
        if max_depth is not None:
            query = query.where(TaxonomyNode.level <= max_depth)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_node(self, data: TaxonomyNodeCreate) -> TaxonomyNode:
        if data.parent_id:
            parent = await self.get_node(data.parent_id)
            if not parent:
                raise TaxonomyServiceError("Parent node not found")
            if parent.branch.value != data.branch:
                raise TaxonomyServiceError("Node branch must match parent branch")
            level = parent.level + 1
            path = f"{parent.path}.{slugify(data.name)}" if parent.path else slugify(data.name)
            governance_group_id = parent.governance_group_id
        else:
            # Root-level node (level 1 = branch, level 2 = governance group)
            # Must provide governance_group context externally for level-2 nodes
            raise TaxonomyServiceError("Nodes must have a parent (use seed for root nodes)")

        node = TaxonomyNode(
            governance_group_id=governance_group_id,
            parent_id=data.parent_id,
            path=path,
            name=data.name,
            slug=slugify(data.name),
            level=level,
            branch=Branch(data.branch),
            definition=data.definition,
            distinguishing_characteristics=data.distinguishing_characteristics,
            inclusions=data.inclusions,
            exclusions=data.exclusions,
            sort_order=data.sort_order,
        )
        self.session.add(node)
        await self.session.flush()
        return node

    async def update_node(self, node_id: str, data: TaxonomyNodeUpdate) -> TaxonomyNode | None:
        node = await self.get_node(node_id)
        if not node:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(node, field, value)
        await self.session.flush()
        return node

    async def delete_node(self, node_id: str) -> bool:
        node = await self.get_node(node_id)
        if not node:
            return False
        if node.children:
            raise TaxonomyServiceError("Cannot delete node with children — delete leaves first")
        await self.session.delete(node)
        await self.session.flush()
        return True

    async def get_subtree(self, node_id: str) -> list[TaxonomyNode]:
        node = await self.get_node(node_id)
        if not node:
            return []
        # Use path prefix matching (works with ltree-style dot-separated paths)
        result = await self.session.execute(
            select(TaxonomyNode)
            .where(TaxonomyNode.path.like(f"{node.path}%"))
            .order_by(TaxonomyNode.path, TaxonomyNode.sort_order)
        )
        return list(result.scalars().all())

    async def get_parent_chain(self, node_id: str) -> list[TaxonomyNode]:
        chain = []
        node = await self.get_node(node_id)
        while node and node.parent_id:
            result = await self.session.execute(
                select(TaxonomyNode).where(TaxonomyNode.id == node.parent_id)
            )
            node = result.scalar_one_or_none()
            if node:
                chain.insert(0, node)
        return chain

    async def resolve_node_path(self, node_id: str) -> str | None:
        """Build a human-readable path like 'Software > Content & Media > Media Production'."""
        node = await self.get_node(node_id)
        if not node:
            return None
        chain = await self.get_parent_chain(node_id)
        names = [n.name for n in chain] + [node.name]
        return " > ".join(names)

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
        return list(result.scalars().all())
