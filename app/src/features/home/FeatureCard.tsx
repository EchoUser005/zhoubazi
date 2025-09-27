import Link from "next/link";

type Props = {
  title: string;
  desc?: string;
  href?: string;
  disabled?: boolean;
  badge?: string;
};

export default function FeatureCard({ title, desc, href, disabled, badge }: Props) {
  const inner = (
    <div
      className={`rounded-lg border border-neutral-800 p-4 transition ${
        disabled ? "opacity-60 cursor-not-allowed" : "hover:border-neutral-600"
      }`}
      aria-disabled={disabled ? true : undefined}
    >
      <div className="flex items-center gap-2">
        <div className="font-medium">{title}</div>
        {badge ? (
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-neutral-800 text-neutral-300">
            {badge}
          </span>
        ) : null}
      </div>
      {desc ? <div className="text-sm text-neutral-400 mt-1">{desc}</div> : null}
    </div>
  );

  if (disabled || !href) {
    return inner;
  }
  return <Link href={href}>{inner}</Link>;
}