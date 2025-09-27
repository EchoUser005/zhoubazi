"""
测试 Langfuse 追踪功能
"""
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schemas import UserInput
from prompt.context_builder import BaziContextBuilder
from agents.weekly_fortune_agent import WeeklyFortuneAgent
from utils.tracing import flush_traces, TRACE_ENABLED

def test_trace_functionality():
    """测试追踪功能"""
    print("🧪 开始测试 Langfuse 追踪功能...")
    print(f"📊 追踪功能状态: {'✅ 已启用' if TRACE_ENABLED else '❌ 未启用'}")
    
    if not TRACE_ENABLED:
        print("⚠️ 追踪功能未启用，请检查环境变量 ENABLE_LANGFUSE_TRACE")
        return
    
    # 创建测试用户输入
    test_user = UserInput(
        birth_time="2001-12-23 13:00:00",
        birth_location="浙江省金华市东阳市",
        name="测试用户",
        gender="女",
        isTai=False,
        city="北京",
        is_lunar=False
    )
    
    print("🏗️ 测试上下文构建...")
    context_builder = BaziContextBuilder()
    context = context_builder.build_context(test_user)
    print(f"✅ 上下文构建完成: {context.name}")
    
    print("🤖 测试周运势 Agent...")
    agent = WeeklyFortuneAgent()
    
    # 测试同步生成
    print("📝 生成运势报告...")
    try:
        report = agent.generate_report(context)
        print(f"✅ 运势报告生成成功，长度: {len(report)} 字符")
        print(f"📄 报告预览: {report[:100]}...")
    except Exception as e:
        print(f"❌ 运势报告生成失败: {e}")
    
    print("🚀 刷新追踪数据...")
    flush_traces()
    print("✅ 追踪数据已发送到 Langfuse")
    
    print("""
🎉 测试完成！
    
📊 查看追踪数据：
1. 访问: https://us.cloud.langfuse.com
2. 使用你的账号登录
3. 查看刚才生成的 traces

🔍 预期看到的追踪记录：
- build_bazi_context (上下文构建)
- generate_fortune_report (运势报告生成)
- llm_router_invoke (LLM 调用)
""")

if __name__ == "__main__":
    test_trace_functionality()