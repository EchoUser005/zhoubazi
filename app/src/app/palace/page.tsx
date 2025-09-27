import FeatureCard from "../../features/home/FeatureCard";
import Section from "../../features/home/Section";

export default function PalacePage() {
  return (
    <div className="mx-auto max-w-6xl">
      <Section title="账户信息" desc="昵称、头像、邮箱、手机号、订阅、设备（占位）">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <FeatureCard title="昵称/头像" disabled />
          <FeatureCard title="关联邮箱/手机号" disabled />
          <FeatureCard title="订阅状态与设备" disabled />
        </div>
      </Section>

      <Section title="档案管理" desc="自己的/家人/朋友/公司/学校（占位）">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <FeatureCard title="人物档案" disabled />
          <FeatureCard title="组织档案" disabled />
          <FeatureCard title="教育档案" disabled />
        </div>
      </Section>

      <Section title="通用设置" desc="语言/模型/记忆开关/推送设置（占位）">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FeatureCard title="偏好设置" disabled />
          <FeatureCard title="推送设置" disabled />
        </div>
      </Section>
    </div>
  );
}