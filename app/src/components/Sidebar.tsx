"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Compass,
  MessageSquare,
  Calendar,
  Boxes,
  User,
} from "lucide-react";

const items = [
  { href: "/", icon: Home, label: "首页" },
  { href: "/discover", icon: Compass, label: "发现" },
  { href: "/dialog", icon: MessageSquare, label: "灵讯" },
  { href: "/timeline", icon: Calendar, label: "时运卷轴" },
  { href: "/vault", icon: Boxes, label: "万象匣" },
  { href: "/minggong", icon: User, label: "命宫" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex md:flex-col w-16 shrink-0 border-r border-neutral-900/70 bg-black fixed left-0 top-0 h-screen z-50">
      <div className="h-14 flex items-center justify-center border-b border-neutral-900/70">
        <div className="w-8 h-8 rounded-full bg-white text-black flex items-center justify-center text-xs font-bold">
          N
        </div>
      </div>
      <nav className="flex-1 py-4 flex flex-col gap-2 items-center overflow-y-auto">
        {items.map(({ href, icon: Icon, label }) => {
          const active =
            pathname === href || (href !== "/" && pathname?.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              data-testid={`sidebar-${label}`}
              className="group flex w-full flex-col items-center gap-1"
              aria-label={label}
              title={label}
            >
              <div
                className={`grid size-12 place-items-center rounded-xl transition
                ${active ? "bg-neutral-900 ring-1 ring-neutral-700" : "hover:bg-neutral-900/60"}`}
              >
                <Icon
                  className={`h-5 w-5 ${
                    active ? "text-white" : "text-neutral-400 group-hover:text-white"
                  }`}
                />
              </div>
              <div
                className={`text-[10px] leading-tight ${
                  active ? "text-white" : "text-neutral-400 group-hover:text-white"
                }`}
              >
                {label}
              </div>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}