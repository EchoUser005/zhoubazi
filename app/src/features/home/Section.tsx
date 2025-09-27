import React from "react";

type Props = {
  title: string;
  desc?: string;
  children: React.ReactNode;
};

export default function Section({ title, desc, children }: Props) {
  return (
    <section className="w-full py-6">
      <header className="mb-4">
        <h2 className="text-xl font-semibold">{title}</h2>
        {desc ? (
          <p className="text-sm text-neutral-400 mt-1">{desc}</p>
        ) : null}
      </header>
      {children}
    </section>
  );
}