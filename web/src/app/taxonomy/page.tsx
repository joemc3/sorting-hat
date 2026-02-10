"use client";

import { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TaxonomyTree } from "@/components/taxonomy-tree";
import { NodeDetail } from "@/components/node-detail";
import { api, type TaxonomyNode, type TaxonomyNodeDetail } from "@/lib/api";

export default function TaxonomyPage() {
  const [nodes, setNodes] = useState<TaxonomyNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<TaxonomyNodeDetail | null>(null);
  const [branch, setBranch] = useState<string>("software");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const fetchNodes = search.length >= 2
      ? api.taxonomy.searchNodes(search)
      : api.taxonomy.listNodes({ branch });
    fetchNodes
      .then((data) => { if (!cancelled) setNodes(data); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [branch, search]);

  const handleBranchChange = (value: string) => {
    setLoading(true);
    setBranch(value);
  };

  const handleSearchChange = (value: string) => {
    setLoading(true);
    setSearch(value);
  };

  const handleSelect = async (node: TaxonomyNode) => {
    const detail = await api.taxonomy.getNode(node.id);
    setSelectedNode(detail);
  };

  return (
    <div className="flex gap-6 h-full">
      <div className="w-96 flex flex-col gap-4">
        <h2 className="text-2xl font-bold">Taxonomy</h2>
        <Input
          placeholder="Search nodes..."
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
        />
        <Tabs value={branch} onValueChange={handleBranchChange}>
          <TabsList className="w-full">
            <TabsTrigger value="software" className="flex-1">Software</TabsTrigger>
            <TabsTrigger value="hardware" className="flex-1">Hardware</TabsTrigger>
          </TabsList>
        </Tabs>
        <ScrollArea className="flex-1">
          {loading ? (
            <p className="text-sm text-muted-foreground p-2">Loading...</p>
          ) : (
            <TaxonomyTree
              nodes={nodes}
              selectedId={selectedNode?.id ?? null}
              onSelect={handleSelect}
              isSearching={search.length >= 2}
            />
          )}
        </ScrollArea>
      </div>
      <div className="flex-1">
        {selectedNode ? (
          <NodeDetail node={selectedNode} />
        ) : (
          <p className="text-muted-foreground">Select a node to view details.</p>
        )}
      </div>
    </div>
  );
}
