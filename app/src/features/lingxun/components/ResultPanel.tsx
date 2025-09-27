"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Loader2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

type Props = {
  isLoading: boolean;
  result: string;
};

export function ResultPanel({ isLoading, result }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>分析结果</CardTitle>
      </CardHeader>
      <CardContent className="prose prose-invert max-w-none min-h-[240px]">
        {isLoading ? (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            正在请求AI大师分析中...
          </div>
        ) : result ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{result}</ReactMarkdown>
        ) : (
          <div className="text-muted-foreground">提交信息后将在此显示分析结果。</div>
        )}
      </CardContent>
    </Card>
  );
}