"use client";

import { Heart, Activity, Coins } from "lucide-react";
import { API_BASE_URL } from "@/config/api";

function ScoreRing({ value, label }: { value: number; label: string }) {
  const v = Math.max(0, Math.min(100, value));
  const getBarColor = (s: number) => (s < 60 ? "bg-red-500" : s < 80 ? "bg-yellow-500" : "bg-lime-500");

  const icon =
    label === "情感" ? <Heart className="h-4 w-4" /> :
    label === "健康" ? <Activity className="h-4 w-4" /> :
    <Coins className="h-4 w-4" />;

  const iconColor =
    label === "情感" ? "text-pink-400" :
    label === "健康" ? "text-blue-400" :
    "text-amber-400";

  return (
    <div className="rounded-xl border border-neutral-800 bg-black/20 p-4">
      <div className="flex items-center gap-3">
        <div className={`h-8 w-8 grid place-items-center rounded-full bg-neutral-900 ${iconColor}`}>
          {icon}
        </div>
        <div className="flex items-center gap-2 text-sm text-neutral-300">
          <span>{label}</span>
          <span className="text-neutral-400">{v}</span>
        </div>
      </div>
      <div className="mt-2 h-2 rounded bg-neutral-800 overflow-hidden">
        <div className={`h-full ${getBarColor(v)}`} style={{ width: `${v}%` }} />
      </div>
    </div>
  );
}

export default function Home() {
  const [scores, setScores] = useState({ emotion: 55, health: 82, wealth: 68 }); // 默认 mock，接口成功后覆盖

  useEffect(() => {
    let aborted = false;
    (async () => {
      try {
        const resp = await fetch(`${API_BASE_URL}/get_fortune_score`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dimension: "流日" }),
        });
        if (!resp.ok) {
          console.warn("[score] http error:", resp.status);
          return;
        }
        const data = await resp.json();
        const r = data?.result;
        if (!aborted && r && typeof r.emotion === "number" && typeof r.health === "number" && typeof r.wealth === "number") {
          setScores({ emotion: r.emotion, health: r.health, wealth: r.wealth });
        }
      } catch (e) {
        console.warn("[score] fetch fail:", e);
      }
    })();
    return () => { aborted = true; };
  }, []);
  const statuses = [
    { title: "运势上升", desc: "今日整体运势呈上升趋势，适合开展新项目。" },
    { title: "情感和谐", desc: "人际关系融洽，适合沟通交流。" },
    { title: "财运平稳", desc: "财务状况稳定，避免大额投资。" },
  ];
  const tips = [
    "今日宜：求职、会议、学习",
    "今日忌：投资、搬家、争执",
    "幸运色：黑色、白色、灰色",
  ];

  return (
    <main className="min-h-[calc(100vh-56px)] px-6 py-10 mx-auto max-w-6xl">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左：三维运势评分 */}
        <section className="lg:col-span-2 rounded-2xl border border-neutral-800 bg-black/30 p-5">
          <div className="mb-1 flex items-center gap-2 text-sm text-neutral-300">
            <svg
              aria-hidden
              className="h-4 w-4 text-neutral-300"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M3 3v18h18" />
              <path d="M7 15l3-3 2 2 5-5" />
            </svg>
            <span className="font-medium">今日三维运势</span>
          </div>
          <div className="text-sm text-neutral-500">
            基于原局命盘与流运作用预测的今日综合运势评分
          </div>

          <div className="mt-6 grid grid-cols-1 gap-8 sm:grid-cols-3">
            <ScoreRing value={scores.emotion} label="情感" />
            <ScoreRing value={scores.health} label="健康" />
            <ScoreRing value={scores.wealth} label="财富" />
          </div>
        </section>

        {/* 右上：今日状态 */}
        <section className="rounded-2xl border border-neutral-800 bg-black/30 p-5">
          <div className="mb-3 flex items-center gap-2 text-sm text-neutral-300">
            <svg
              aria-hidden
              className="h-4 w-4 text-neutral-300"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="4" />
              <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
            </svg>
            <span className="font-medium">今日状态</span>
          </div>
          <div className="space-y-3">
            {statuses.map((s, i) => (
              <div key={i} className="rounded-xl border border-neutral-800 bg-black/20 p-3">
                <div className="text-sm text-white">{s.title}</div>
                <div className="text-sm text-neutral-400 mt-1">{s.desc}</div>
              </div>
            ))}
          </div>
        </section>

        {/* 右下：温馨提示 */}
        <section className="rounded-2xl border border-neutral-800 bg-black/30 p-5 lg:col-start-3">
          <div className="mb-3 flex items-center gap-2 text-sm text-neutral-300">
            <svg
              aria-hidden
              className="h-4 w-4 text-neutral-300"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2l1.5 4.5L18 8l-4.5 1.5L12 14l-1.5-4.5L6 8l4.5-1.5L12 2z" />
            </svg>
            <span className="font-medium">温馨提示</span>
          </div>
          <ul className="space-y-2 text-sm text-neutral-400">
            {tips.map((t, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-[6px] inline-block h-1.5 w-1.5 rounded-full bg-neutral-500" />
                <span>{t}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </main>
  );
}

import { useEffect, useState } from "react";