"use client";

import { useState } from "react";
import { ClassifyForm } from "@/components/classify-form";
import { ClassificationResult } from "@/components/classification-result";
import { api, type ClassificationDetail } from "@/lib/api";

export default function ClassifyPage() {
  const [result, setResult] = useState<ClassificationDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClassify = async (url: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const classification = await api.classify.submit(url);
      const detail = await api.classify.get(classification.id);
      setResult(detail);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Classification failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl space-y-6">
      <h2 className="text-2xl font-bold">Classify a Product</h2>
      <p className="text-muted-foreground">
        Paste a product URL to classify it into the taxonomy.
      </p>
      <ClassifyForm onSubmit={handleClassify} loading={loading} />
      {error && (
        <div className="text-sm text-destructive bg-destructive/10 p-3 rounded">
          {error}
        </div>
      )}
      {result && <ClassificationResult result={result} />}
    </div>
  );
}
