import Section from "../../features/home/Section";
import FeatureCard from "../../features/home/FeatureCard";

export default function TimelinePage() {
  return (
    <div className="mx-auto max-w-6xl">
      <Section title="时运卷轴" desc="万年历可视化（占位）">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FeatureCard title="时间轴总览" desc="按年/月/日切换（占位）" disabled />
          <FeatureCard title="冲克分析" desc="五行冲克标注（占位）" disabled />
        </div>
      </Section>
    </div>
  );
}