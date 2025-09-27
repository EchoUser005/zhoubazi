"use client";

import { useState } from "react";
import MessageList from "../../features/dialog/MessageList";
import ChatPanel from "@/features/dialog/ChatPanel";
import FeatureCard from "../../features/home/FeatureCard";
import Section from "../../features/home/Section";

export default function DialogHubPage() {
  const mockMessages = [
    {
      id: "m1",
      type: "lingxun_report",
      title: "周运录 · 本周运势",
      preview: "综合 78 · 事业顺势，情感稳定，注意作息与饮食均衡。",
      time: new Date().toISOString(),
      unread: true,
    },
    {
      id: "m2",
      type: "ai_bot",
      title: "命理师 · 扶摇子",
      preview: "你好，我是你的 AI 命理师。最近有什么想了解的？",
      time: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    },
    {
      id: "m3",
      type: "dm",
      title: "玄友 · 林舟",
      preview: "这周财运还不错，有空聊聊？",
      time: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    },
  ] as const;

  const [selectedId, setSelectedId] = useState<string | null>(mockMessages[0]?.id ?? null);
  const selected = mockMessages.find((m) => m.id === selectedId) ?? null;

  return (
    <main className="min-h-[calc(100vh-56px)] px-6 py-10 mx-auto max-w-6xl">
      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-4">
        {/* 左侧消息列表 */}
        <aside className="rounded-xl border border-neutral-800 bg-transparent p-3">
          <div className="px-2 pb-2 text-sm text-neutral-400">对话</div>
          <MessageList
            data={mockMessages as any}
            onSelect={(id) => setSelectedId(id)}
            selectedId={selectedId ?? undefined}
          />
        </aside>

        {/* 右侧聊天面板 */}
        <section className="rounded-xl border border-neutral-800 bg-transparent p-0">
          <ChatPanel msg={selected} />
        </section>
      </div>
    </main>
  );
}