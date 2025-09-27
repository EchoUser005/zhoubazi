import os
import sys
from jinja2 import Template

# 将项目根目录添加到 Python 路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentic_analyse import LLM_Chat
from schemas import BaziContext

def test_predict_fortune_prompt():
    """
    用于测试 agetnic_analyse.py 中 LLM_Chat 类的功能，
    特别是针对 predict_fortune.md 这个 prompt 的效果。
    """
    print("--- 开始测试 predict_fortune.md Prompt ---")

    # 1. 加载 Prompt 模板
    prompt_path = os.path.join(os.path.dirname(__file__), "predict_fortune.md")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template_str = f.read()
    
    template = Template(prompt_template_str)

    # 2. 构造一个模拟的 BaziContext 对象 (使用与之前测试相似的数据)
    # 在实际测试中，您可以修改这些值来测试不同的命盘情况
    mock_context = BaziContext(
        nowtime="甲辰年庚午月",
        calendar="周一 甲子日 6月24日\\n周二 乙丑日 6月25日...",
        name="模拟用户",
        gender="女",
        isTai="否",
        birth_correct="公历 2001年12月23日 13:00 辛巳年 庚子月 辛酉日 乙未时",
        city="北京",
        bazi="辛巳 庚子 辛酉 乙未",
        dayun_time="8岁 2009年 辛丑 -> 18岁 2019年 壬寅 -> ...",
        qiyun_time="出生后7年10月15日 上大运",
        jiaoyun_time="逢丙、辛年 11月8日交大运"
    )

    # 3. 渲染 Prompt
    # 我们可以为 'dimention' 传入不同的值来测试不同方面的预测
    dimention_to_test = "财富" # 您可以改为 "感情" 或 "健康"
    
    rendered_prompt = template.render(
        dimention=dimention_to_test,
        **mock_context.model_dump()
    )

    print(f"\\n--- 正在测试维度: {dimention_to_test} ---")
    # print("\\n--- 渲染后的 Prompt (部分内容) ---")
    # print(rendered_prompt[:500] + "...") # 打印部分渲染后的 prompt 供检查

    # 4. 初始化 LLM_Chat 并调用
    try:
        llm_chat = LLM_Chat()
        
        print("\n--- 正在调用 AI 进行分析，请稍候... ---")
        
        # 这里我们直接使用 get_full_response 来获取完整的 JSON 输出
        # 注意：入参必须是 BaziContext，而不是字符串
        analysis_result = llm_chat.get_full_response(mock_context)
        
        print("\n--- AI 返回的原始结果 ---")
        print(analysis_result)
    except Exception as e:
        print(f"\\n--- 测试过程中发生错误 ---")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        print("请检查您的 API 密钥、网络连接以及 agentic_analyse.py 中的代码。")

    print("\\n--- 测试结束 ---")

    # 使用 FortuneScoreAgent 直接测试 predict_fortune.md（与服务层一致）
    from agents.fortune_score_agent import FortuneScoreAgent
    agent = FortuneScoreAgent()  # 默认使用 predict_fortune.md + 路由默认 gemini
    scores = agent.predict_scores(mock_context, dimension="流日")
    print("\n--- 评分结果 ---")
    print(scores)
    dimension_to_test = "流月"  # 可改为 "流日" 以验证流日干支注入
    print(f"\n--- 正在测试维度: {dimension_to_test} ---")
    try:
        scores = agent.predict_scores(mock_context, dimension=dimension_to_test)
        print("\n--- 预测分数 ---")
        print(scores)
    except Exception as e:
        print("\n--- 测试过程中发生错误 ---")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        print("请检查 API Key/网络 与 agents/fortune_score_agent.py 中模型配置。")

if __name__ == "__main__":
    test_predict_fortune_prompt()