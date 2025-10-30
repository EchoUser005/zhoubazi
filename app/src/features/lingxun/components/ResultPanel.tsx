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
        {/* ✅ 关键改动：改进了条件渲染逻辑 */}
        {result && isLoading ? (
          // 有内容但还在加载：显示内容 + 加载指示器
          <div>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{result}</ReactMarkdown>
            <div className="flex items-center gap-2 text-muted-foreground mt-4 text-sm">
              <Loader2 className="h-4 w-4 animate-spin" />
              继续生成中...
            </div>
          </div>
        ) : isLoading ? (
          // 还在加载，没有内容
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            正在请求AI大师分析中...
          </div>
        ) : result ? (
          // 完成了，有内容
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{result}</ReactMarkdown>
        ) : (
          // 没有任何内容
          <div className="text-muted-foreground">提交信息后将在此显示分析结果。</div>
        )}
      </CardContent>
    </Card>
  );
}