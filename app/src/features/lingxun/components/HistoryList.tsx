"use client";

import { History } from "lucide-react";
import type { HistoryEntry } from "../../lingxun/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type Props = {
  history: HistoryEntry[];
  onSelect: (entry: HistoryEntry) => void;
};

export function HistoryList({ history, onSelect }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <History className="h-5 w-5" />
          历史记录（最近 5 条）
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {history.length === 0 ? (
          <div className="text-sm text-muted-foreground">暂无历史记录</div>
        ) : history.map((h) => (
          <div key={h.id} className="flex items-center justify-between border-b border-border pb-2 last:border-0 last:pb-0">
            <div className="text-sm">
              <div className="font-medium">{h.name || "未填写"}</div>
              <div className="text-muted-foreground">{h.birth_location}</div>
            </div>
            <Button variant="outline" size="sm" onClick={() => onSelect(h)}>填充</Button>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}