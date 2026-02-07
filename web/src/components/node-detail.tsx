import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { TaxonomyNodeDetail } from "@/lib/api";

interface NodeDetailProps {
  node: TaxonomyNodeDetail;
}

export function NodeDetail({ node }: NodeDetailProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
          {node.parent_chain.map((p, i) => (
            <span key={p.id}>
              {i > 0 && " > "}
              {p.name}
            </span>
          ))}
          {node.parent_chain.length > 0 && " > "}
        </div>
        <CardTitle className="flex items-center gap-2">
          {node.name}
          <Badge variant={node.branch === "software" ? "default" : "secondary"}>
            {node.branch}
          </Badge>
          <Badge variant="outline">Level {node.level}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {node.definition && (
          <div>
            <h4 className="font-medium text-sm mb-1">Definition</h4>
            <p className="text-sm text-muted-foreground">{node.definition}</p>
          </div>
        )}
        {node.distinguishing_characteristics && (
          <div>
            <h4 className="font-medium text-sm mb-1">Distinguishing Characteristics</h4>
            <p className="text-sm text-muted-foreground">
              {node.distinguishing_characteristics}
            </p>
          </div>
        )}
        {node.inclusions && (
          <div>
            <h4 className="font-medium text-sm mb-1">Includes</h4>
            <p className="text-sm text-muted-foreground">{node.inclusions}</p>
          </div>
        )}
        {node.exclusions && (
          <div>
            <h4 className="font-medium text-sm mb-1">Does Not Include</h4>
            <p className="text-sm text-muted-foreground">{node.exclusions}</p>
          </div>
        )}
        {node.children.length > 0 && (
          <>
            <Separator />
            <div>
              <h4 className="font-medium text-sm mb-2">
                Children ({node.children.length})
              </h4>
              <div className="flex flex-wrap gap-1">
                {node.children.map((child) => (
                  <Badge key={child.id} variant="outline">
                    {child.name}
                  </Badge>
                ))}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
