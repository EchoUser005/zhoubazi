import FeatureCard from "../../features/home/FeatureCard";
import Section from "../../features/home/Section";

export default function VaultPage() {
  return (
    <div className="mx-auto max-w-6xl">
      <Section title="万象匣" desc="系统案例库与自建知识库（占位）">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FeatureCard title="系统案例库" disabled />
          <FeatureCard title="自建知识库" disabled />
        </div>
      </Section>
    </div>
  );
}