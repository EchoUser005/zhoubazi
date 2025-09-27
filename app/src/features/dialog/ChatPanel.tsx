"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { UserRound, LineChart, Send } from "lucide-react";
import { useRouter } from "next/navigation";
import type { Message } from "./MessageItem";

export default function ChatPanel({ msg }: { msg: Message | null }) {
  const router = useRouter();

  type Bubble = { id: string; role: "user" | "peer"; text: string; time: string };

  // 初始仅在非“周运录”时给一条 peer 气泡
  const [bubbles, setBubbles] = useState<Bubble[]>(
    msg && msg.type !== "lingxun_report" ? [{ id: "b1", role: "peer", text: msg.preview, time: msg.time }] : []
  );
  const [input, setInput] = useState("");

  // 切换左侧选中消息时重置聊天区（保证 Hooks 顺序稳定）
  useEffect(() => {
    if (!msg || msg.type === "lingxun_report") {
      setBubbles([]);
      setInput("");
      return;
    }
    setBubbles([{ id: "b1", role: "peer", text: msg.preview, time: msg.time }]);
    setInput("");
  }, [msg?.id, msg?.type]);

  if (!msg) {
    return <div className="p-6 text-neutral-400">从左侧选择一条消息查看详情。</div>;
  }

  // 周运录：简洁面板 + 按钮跳转（恢复最初形态）
  if (msg.type === "lingxun_report") {
    return (
      <div className="flex h-full min-h-[480px] flex-col">
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-neutral-800 px-4 py-3">
          <div className="h-10 w-10 rounded-full bg-neutral-900 text-emerald-400 grid place-items-center">
            <LineChart className="h-5 w-5" />
          </div>
          <div>
            <div className="font-semibold">{msg.title || "周运录"}</div>
            <div className="text-xs text-neutral-500">{new Date(msg.time).toLocaleString()}</div>
          </div>
        </div>

        {/* Preview */}
        <div className="flex-1 overflow-auto p-4">
          <div className="rounded-lg border border-neutral-800 bg-neutral-950/40 p-4">
            <div className="text-sm text-neutral-300">{msg.preview}</div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-neutral-800 p-3">
          <div className="flex items-center justify-between">
            <div className="text-xs text-neutral-500">查看或生成你的周运势分析</div>
            <Button onClick={() => router.push("/lingxun")} className="bg-emerald-600 hover:bg-emerald-500">
              前往周运录
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // 标准聊天区（扶摇子/玄友）
  const send = () => {
    const text = input.trim();
    if (!text) return;
    const now = new Date().toISOString();
    setBubbles((bs) => [...bs, { id: crypto.randomUUID(), role: "user", text, time: now }]);
    setInput("");
    setTimeout(() => {
      setBubbles((bs) => [
        ...bs,
        {
          id: crypto.randomUUID(),
          role: "peer",
          text: "已收到，我会结合你的生辰信息给出建议（占位回复）。",
          time: new Date().toISOString(),
        },
      ]);
    }, 500);
  };

  const HeaderAvatar =
    msg.type === "ai_bot" ? (
      <div className="h-10 w-10 rounded-full overflow-hidden">
        <img src="/扶摇子.jpg" alt="扶摇子" className="h-10 w-10 object-cover" />
      </div>
    ) : (
      <div className="h-10 w-10 rounded-full bg-neutral-900 text-neutral-300 grid place-items-center">
        <UserRound className="h-5 w-5" />
      </div>
    );

  return (
    <div className="flex h-full min-h-[480px] flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-neutral-800 px-4 py-3">
        {HeaderAvatar}
        <div>
          <div className="font-semibold">{msg.title}</div>
          <div className="text-xs text-neutral-500">{new Date(msg.time).toLocaleString()}</div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-3">
        {bubbles.map((b) => (
          <div key={b.id} className={`flex ${b.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[70%] rounded-2xl px-3 py-2 text-sm ${
                b.role === "user"
                  ? "bg-neutral-100 text-neutral-900"
                  : "bg-neutral-900 text-neutral-200 border border-neutral-800"
              }`}
            >
              <div>{b.text}</div>
              <div className="mt-1 text-[10px] opacity-60">{new Date(b.time).toLocaleTimeString()}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Composer */}
      <div className="border-t border-neutral-800 p-3">
        <div className="flex items-end gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入内容，按发送开始对话…"
            className="min-h-[44px]"
          />
          <Button onClick={send} className="h-[44px]" disabled={!input.trim()}>
            <Send className="h-4 w-4 mr-1" />
            发送
          </Button>
        </div>
      </div>
    </div>
  );
}