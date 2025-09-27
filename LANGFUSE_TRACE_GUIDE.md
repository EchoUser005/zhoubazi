# Langfuse 追踪功能使用指南

## 概述

本项目已集成 Langfuse 追踪功能，可以监控和分析所有核心组件的执行情况，包括：

- 🤖 LLM 调用（Gemini/DeepSeek）
- 🎯 Agent 动作（周运势分析、运势打分）
- 🔧 API 调用
- 📊 上下文构建

## 已追踪的组件

### 1. API 端点
- `/analyze` - 运势分析
- `/predict_fortune` - 运势预测打分
- `/analyze/stream` - 流式运势分析
- `/get_fortune_score` - 获取运势分数
- `/calc_bazi` - 八字计算

### 2. Agent 组件
- **WeeklyFortuneAgent**
  - `generate_report()` - 生成周运势报告
  - `stream_report()` - 流式生成报告

- **FortuneScoreAgent**
  - `predict_scores()` - 预测运势评分

- **BaziContextBuilder**
  - `build_context()` - 构建八字上下文

### 3. LLM 调用
- **LLMRouter**
  - `invoke()` - 同步调用
  - `stream()` - 流式调用
  - `invoke_reasoning()` - 推理调用

- **LLM_Chat（agentic_analyse.py）**
  - `stream_chat()` - 流式对话
  - `get_full_response()` - 获取完整响应

## 配置

### 环境变量

在 `.env` 文件中配置：

```bash
# 启用/禁用追踪功能
ENABLE_LANGFUSE_TRACE=true

# Langfuse 服务配置
LANGFUSE_SECRET_KEY=sk-lf-7bf3c263-7060-4a52-ad75-2d13cbd0878c
LANGFUSE_PUBLIC_KEY=pk-lf-b5a53044-8e15-450e-a15a-83f146505206
LANGFUSE_HOST=https://us.cloud.langfuse.com

# 调试模式（可选）
LANGFUSE_DEBUG=false
```

### 禁用追踪

如果不需要追踪功能，可以：

1. 设置环境变量：`ENABLE_LANGFUSE_TRACE=false`
2. 或者不安装 langfuse 包

## 查看追踪数据

1. 访问 Langfuse 控制台：https://us.cloud.langfuse.com
2. 使用提供的 public key 登录
3. 查看实时的执行追踪、性能指标和错误日志

## 追踪数据包含的信息

### 对于每个函数调用
- **基础信息**：函数名、模块名、执行时间
- **输入数据**：参数数量、关键字参数键名
- **输出数据**：返回值类型、执行状态
- **错误信息**：异常类型和错误消息（如果有）
- **性能指标**：执行时长（秒）

### 对于 Agent 动作
- **Agent 类型**：weekly_fortune、fortune_score、context_builder
- **动作名称**：具体执行的方法名
- **执行状态**：成功或失败

### 对于 API 调用
- **端点名称**：API 路径
- **调用类型**：api_call
- **请求信息**：参数统计
- **响应信息**：结果类型和状态

## 性能优势

通过 Langfuse 追踪，你可以：

1. **监控性能**：识别慢查询和瓶颈
2. **错误追踪**：快速定位和诊断问题
3. **使用分析**：了解用户行为和系统使用模式
4. **质量保证**：确保 LLM 输出质量和一致性

## 故障排除

### 常见问题

1. **Langfuse 初始化失败**
   - 检查网络连接
   - 验证 API 密钥是否正确
   - 确认 Langfuse 服务可访问

2. **追踪数据未显示**
   - 确认 `ENABLE_LANGFUSE_TRACE=true`
   - 检查控制台是否有错误消息
   - 手动调用 `flush_traces()` 确保数据发送

3. **性能影响**
   - 追踪功能对性能影响极小
   - 如有需要可通过环境变量禁用

## 示例用法

### 在新组件中添加追踪

```python
from utils.tracing import trace_llm_call, trace_agent_action

class MyAgent:
    @trace_agent_action(name="my_custom_action", agent_type="custom")
    def my_method(self, data):
        # 你的代码
        return result

    @trace_llm_call(name="my_llm_call")
    def call_llm(self, prompt):
        # LLM 调用代码
        return response
```

### 手动创建追踪

```python
from utils.tracing import create_trace

# 手动记录重要操作
create_trace(
    name="custom_operation",
    input_data={"param": "value"},
    output_data={"result": "success"},
    duration=1.5,
    metadata={"category": "business_logic"}
)
```

## 更新日志

- ✅ 集成 Langfuse SDK
- ✅ 添加核心组件追踪装饰器
- ✅ 配置 API 生命周期管理
- ✅ 创建环境变量配置模板
- ✅ 提供完整的使用文档

---

🎉 恭喜！你的项目现在已经具备了完整的 Langfuse 追踪功能！