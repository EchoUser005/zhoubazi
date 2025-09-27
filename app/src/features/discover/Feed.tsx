import PostCard, { type Post } from "./PostCard";

export default function Feed() {
  const posts: Post[] = [
    {
      id: "p1",
      author: "扶摇子",
      title: "本周运势节气提醒",
      content: "临近白露，注意作息与情绪管理。金旺木衰，适合收敛与复盘。",
      time: new Date().toISOString(),
      likes: 128,
      comments: 23,
      favorites: 41,
    },
    {
      id: "p2",
      author: "知音阁 · 推荐",
      content: "精选问卜：求学与择业该如何抉择？欢迎在评论区分享你的建议。",
      time: new Date(Date.now() - 1000 * 60 * 50).toISOString(),
      likes: 76,
      comments: 12,
      favorites: 19,
    },
    {
      id: "p3",
      author: "玄友 · 林舟",
      title: "开业择吉讨论",
      content: "计划农历九月初六开业，求鉴冲克与喜忌。",
      time: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
      likes: 45,
      comments: 8,
      favorites: 6,
    },
  ];

  return (
    <div className="space-y-4">
      {posts.map((p) => (
        <PostCard key={p.id} post={p} />
      ))}
    </div>
  );
}