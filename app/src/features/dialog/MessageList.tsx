"use client";

import MessageItem, { type Message } from "./MessageItem";

export default function MessageList({ data, onSelect, selectedId }: { data: Message[]; onSelect?: (id: string) => void; selectedId?: string }) {
  return (
    <div className="space-y-3">
      {data.map((m) => (
        <MessageItem key={m.id} msg={m} onSelect={onSelect} selected={m.id === selectedId} />
      ))}
    </div>
  );
}