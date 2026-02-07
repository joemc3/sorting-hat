"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface ClassifyFormProps {
  onSubmit: (url: string) => void;
  loading: boolean;
}

export function ClassifyForm({ onSubmit, loading }: ClassifyFormProps) {
  const [url, setUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) onSubmit(url.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        type="url"
        placeholder="https://example.com/product"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        className="flex-1"
        required
      />
      <Button type="submit" disabled={loading || !url.trim()}>
        {loading ? "Classifying..." : "Classify"}
      </Button>
    </form>
  );
}
