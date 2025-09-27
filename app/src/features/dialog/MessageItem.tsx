"use client";

import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
// 去掉 Badge 引入
import { Bot, UserRound, LineChart } from "lucide-react";
import { toast } from "sonner";

export type Message = {
  id: string;
  type: "lingxun_report" | "ai_bot" | "dm";
  title: string;
  preview: string;
  time: string; // ISO 字符串
  unread?: boolean;
  from?: string;
};

export default function MessageItem({ msg, onSelect, selected }: { msg: Message; onSelect?: (id: string) => void; selected?: boolean }) {
  const router = useRouter();

  // 仅保留 icon，不再计算“标签/强调色”
  const { icon: Icon } = (() => {
    switch (msg.type) {
      case "lingxun_report":
        return { icon: LineChart };
      case "ai_bot":
        return { icon: Bot };
      default:
        return { icon: UserRound };
    }
  })();

  const handleClick = () => {
    if (msg.type === "lingxun_report") {
      // 仍然保持在右侧显示，不跳路由
      onSelect?.(msg.id);
      return;
    }
    onSelect?.(msg.id);
    toast.info("功能即将上线", { description: "当前为占位入口（避免误触发）。" });
  };

  const avatar = (() => {
    if (msg.type === "ai_bot") {
      // 扶摇子头像保留
      return (
        <div className="h-10 w-10 rounded-full overflow-hidden bg-neutral-900">
          <img src="/扶摇子.jpg" alt="扶摇子" className="h-10 w-10 object-cover" />
        </div>
      );
    }
    if (msg.type === "lingxun_report") {
      // 灵讯改为中性色图标
      return (
        <div className="h-10 w-10 rounded-full bg-neutral-900 flex items-center justify-center text-neutral-300" aria-hidden>
          <Icon className="h-5 w-5" />
        </div>
      );
    }
    // 玄友：系统默认头像
    return (
      <div className="h-10 w-10 rounded-full bg-neutral-900 text-neutral-300 grid place-items-center">
        <UserRound className="h-5 w-5" />
      </div>
    );
  })();

  // 格式化时间
  const time = new Date(msg.time).toLocaleString();

  return (
    <Card
      onClick={handleClick}
      className={`p-4 cursor-pointer border-neutral-800 hover:border-neutral-600 transition ${
        msg.unread ? "bg-neutral-950/60" : ""
      } ${selected ? "ring-1 ring-neutral-600 border-neutral-700" : ""}`}
    >
      <div className="flex items-start gap-3">
        {avatar}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <div className="font-medium truncate">{msg.title}</div>
            {/* 移除类型 Badge（周运录/AI/真人） */}
          </div>
          <div className="text-sm text-neutral-400 truncate mt-0.5">{msg.preview}</div>
        </div>
        <div className="text-xs text-neutral-500 whitespace-nowrap">{time}</div>
      </div>
    </Card>
  );
}