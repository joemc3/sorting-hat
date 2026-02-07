const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export interface GovernanceGroup {
  id: string;
  name: string;
  slug: string;
  description: string;
  covers_software: boolean;
  covers_hardware: boolean;
  sort_order: number;
}

export interface TaxonomyNode {
  id: string;
  governance_group_id: string;
  parent_id: string | null;
  path: string;
  name: string;
  slug: string;
  level: number;
  branch: "software" | "hardware";
  definition: string;
  distinguishing_characteristics: string;
  inclusions: string;
  exclusions: string;
  sort_order: number;
}

export interface TaxonomyNodeDetail extends TaxonomyNode {
  children: TaxonomyNode[];
  parent_chain: TaxonomyNode[];
}

export interface ClassificationResult {
  id: string;
  url: string;
  product_summary: string;
  primary_node_id: string | null;
  primary_node_path: string | null;
  secondary_node_ids: string[];
  confidence_score: number | null;
  model_used: string;
  reasoning: string;
  created_at: string;
}

export interface ClassificationStep {
  id: string;
  step_type: "scrape" | "summarize" | "classify";
  input_text: string;
  output_text: string;
  model_used: string;
  tokens_used: number;
  latency_ms: number;
}

export interface ClassificationDetail extends ClassificationResult {
  raw_content: string;
  steps: ClassificationStep[];
}

export const api = {
  taxonomy: {
    listGroups: () => fetchAPI<GovernanceGroup[]>("/taxonomy/governance-groups"),
    listNodes: (params?: { branch?: string; governance_group?: string }) => {
      const query = new URLSearchParams();
      if (params?.branch) query.set("branch", params.branch);
      if (params?.governance_group) query.set("governance_group", params.governance_group);
      const qs = query.toString();
      return fetchAPI<TaxonomyNode[]>(`/taxonomy/nodes${qs ? `?${qs}` : ""}`);
    },
    getNode: (id: string) => fetchAPI<TaxonomyNodeDetail>(`/taxonomy/nodes/${id}`),
    searchNodes: (q: string) => fetchAPI<TaxonomyNode[]>(`/taxonomy/nodes/search?q=${encodeURIComponent(q)}`),
  },
  classify: {
    submit: (url: string, model?: string) =>
      fetchAPI<ClassificationResult>("/classify", {
        method: "POST",
        body: JSON.stringify({ url, model }),
      }),
    get: (id: string) => fetchAPI<ClassificationDetail>(`/classify/${id}`),
    list: (params?: { url?: string; limit?: number; offset?: number }) => {
      const query = new URLSearchParams();
      if (params?.url) query.set("url", params.url);
      if (params?.limit) query.set("limit", String(params.limit));
      if (params?.offset) query.set("offset", String(params.offset));
      const qs = query.toString();
      return fetchAPI<ClassificationResult[]>(`/classify${qs ? `?${qs}` : ""}`);
    },
  },
};
