"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { ClassificationDetail } from "@/lib/api";

interface ClassificationResultProps {
  result: ClassificationDetail;
}

export function ClassificationResult({ result }: ClassificationResultProps) {
  const [showSteps, setShowSteps] = useState(false);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Classification Result</CardTitle>
        <p className="text-sm text-muted-foreground">{result.url}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="font-medium text-sm mb-1">Product Summary</h4>
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
            {result.product_summary}
          </p>
        </div>

        <Separator />

        <div>
          <h4 className="font-medium text-sm mb-2">Primary Classification</h4>
          {result.primary_node_path ? (
            <Badge>{result.primary_node_path}</Badge>
          ) : (
            <p className="text-sm text-muted-foreground">No classification</p>
          )}
        </div>

        {result.secondary_node_ids.length > 0 && (
          <div>
            <h4 className="font-medium text-sm mb-2">Secondary Classifications</h4>
            <div className="flex gap-1">
              {result.secondary_node_ids.map((id) => (
                <Badge key={id} variant="outline">{id}</Badge>
              ))}
            </div>
          </div>
        )}

        {result.confidence_score !== null && (
          <div>
            <h4 className="font-medium text-sm mb-1">Confidence</h4>
            <p className="text-sm">{(result.confidence_score * 100).toFixed(0)}%</p>
          </div>
        )}

        {result.reasoning && (
          <div>
            <h4 className="font-medium text-sm mb-1">Reasoning</h4>
            <p className="text-sm text-muted-foreground">{result.reasoning}</p>
          </div>
        )}

        <Separator />

        <button
          onClick={() => setShowSteps(!showSteps)}
          className="text-sm text-primary hover:underline"
        >
          {showSteps ? "Hide" : "Show"} pipeline details ({result.steps.length} steps)
        </button>

        {showSteps && (
          <div className="space-y-3">
            {result.steps.map((step) => (
              <Card key={step.id}>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="outline">{step.step_type}</Badge>
                    <span className="text-xs text-muted-foreground">
                      {step.latency_ms}ms
                      {step.tokens_used > 0 && ` \u00B7 ${step.tokens_used} tokens`}
                      {step.model_used && ` \u00B7 ${step.model_used}`}
                    </span>
                  </div>
                  <pre className="text-xs bg-muted p-2 rounded overflow-auto max-h-48">
                    {step.output_text.slice(0, 2000)}
                  </pre>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
