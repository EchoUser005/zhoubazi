"use client";

import { useState } from "react";
import Compose from "../../features/discover/Compose";
import Feed from "../../features/discover/Feed";
import FeatureCard from "../../features/home/FeatureCard";

export default function DiscoverPage() {
  const [tab, setTab] = useState<"zhiyin" | "xuanji">("zhiyin");

  return (
    <main className="min-h-[calc(100vh-56px)] px-6 py-10 mx-auto max-w-6xl">
      {/* Tabs */}
      <div className="mb-6 overflow-x-auto">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setTab("zhiyin")}
            className={`inline-flex h-8 items-center rounded-full px-3 text-sm transition
              ${tab === "zhiyin"
                ? "border border-neutral-700 bg-neutral-900/60 text-white hover:bg-neutral-900"
                : "border border-neutral-800 bg-transparent text-neutral-400 hover:bg-neutral-900/40"}`}
          >
            知音阁
          </button>
          <button
            type="button"
            onClick={() => setTab("xuanji")}
            className={`inline-flex h-8 items-center rounded-full px-3 text-sm transition
              ${tab === "xuanji"
                ? "border border-neutral-700 bg-neutral-900/60 text-white hover:bg-neutral-900"
                : "border border-neutral-800 bg-transparent text-neutral-400 hover:bg-neutral-900/40"}`}
          >
            玄机库
          </button>
        </div>
      </div>

      {/* Content */}
      {tab === "zhiyin" ? (
        <div className="lg:col-span-2">
          <Compose />
          <Feed />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <FeatureCard title="择吉日" />
          <FeatureCard title="起佳名" />
          <FeatureCard title="合姻缘" />
          <FeatureCard title="找贵人" />
        </div>
      )}
    </main>
  );
}