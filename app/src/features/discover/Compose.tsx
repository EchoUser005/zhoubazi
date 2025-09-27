"use client";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export default function Compose() {
  return (
    <div className="mb-4 rounded-xl border border-neutral-800 bg-transparent p-4">
      <div className="mb-3 flex items-center gap-2 text-sm text-neutral-400">
        {/* 简洁图标（内联 SVG） */}
        <svg
          aria-hidden
          className="h-4 w-4 text-neutral-400"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 19l-7 2 2-7L17 4a2.828 2.828 0 1 1 4 4L11 18z" />
        </svg>
        <span>问卜</span>
      </div>

      <Textarea placeholder="问卜：输入你的问题..." className="mb-3" />
      <div className="flex justify-end">
        <Button variant="secondary" className="opacity-70 cursor-not-allowed" aria-disabled>
          发布
        </Button>
      </div>
    </div>
  );
}