"use client";

import { Button } from "@/components/ui/button";
import { MessageCircle, Heart, Star, Bot, Compass, UserRound, User } from "lucide-react";
import { useState } from "react";

export type Post = {
  id: string;
  author: string;
  title?: string;
  content: string;
  time: string; // ISO
  likes: number;
  comments: number;
  favorites: number;
};

export default function PostCard({ post }: { post: Post }) {
  const [likes, setLikes] = useState(post.likes);
  const [favs, setFavs] = useState(post.favorites);
  const [liked, setLiked] = useState(false);
  const [fav, setFav] = useState(false);

  const likeCount = post.likes + (liked ? 1 : 0);
  const favCount = post.favorites + (fav ? 1 : 0);
  const time = new Date(post.time).toLocaleString();

  const meta = (() => {
    if (post.author.includes("扶摇子")) return { accent: "text-cyan-400", bg: "bg-cyan-900/30", icon: Bot };
    if (post.author.includes("知音阁")) return { accent: "text-emerald-400", bg: "bg-emerald-900/30", icon: Compass };
    if (post.author.includes("玄友")) return { accent: "text-indigo-400", bg: "bg-indigo-900/30", icon: UserRound };
    return { accent: "text-neutral-400", bg: "bg-neutral-900", icon: User };
  })();
  const Icon = meta.icon;

  return (
    <div className="rounded-xl border border-neutral-800 bg-transparent p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <div className={`h-10 w-10 rounded-full ${meta.bg} ${meta.accent} grid place-items-center`} aria-hidden>
            <Icon className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <div className="font-medium">{post.author}</div>
              <div className="text-xs text-neutral-500 whitespace-nowrap">{time}</div>
            </div>
            {post.title ? <div className="mt-1 font-medium">{post.title}</div> : null}
            <div className="mt-1 text-sm text-neutral-300 whitespace-pre-wrap">
              {post.content}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-3 flex items-center gap-4 text-sm text-neutral-400">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setLiked((v) => !v)}
          className={`h-8 px-2 ${liked ? "text-white" : ""}`}
        >
          <Heart className={`h-4 w-4 ${liked ? "fill-current" : ""}`} />
          <span className="ml-1">{likeCount}</span>
        </Button>
        <Button variant="ghost" size="sm" className="h-8 px-2">
          <MessageCircle className="h-4 w-4" />
          <span className="ml-1">{post.comments}</span>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setFav((v) => !v)}
          className={`h-8 px-2 ${fav ? "text-white" : ""}`}
        >
          <Star className={`h-4 w-4 ${fav ? "fill-current" : ""}`} />
          <span className="ml-1">{favCount}</span>
        </Button>
      </div>
    </div>
  );
}