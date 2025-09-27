"""Langfuse 追踪工具模块 - 简化版
提供统一的 trace 和 span 管理功能
"""
import os
import functools
import json
import time
from typing import Any, Dict, Optional, Callable
from datetime import datetime

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    Langfuse = None
    print("警告: langfuse 未安装，trace 功能将被禁用")


class LangfuseTracer:
    """Langfuse 追踪器单例"""
    
    _instance = None
    _langfuse = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.enabled = LANGFUSE_AVAILABLE and self._should_enable_trace()
        
        if self.enabled and Langfuse is not None:
            try:
                self._langfuse = Langfuse(
                    secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-lf-7bf3c263-7060-4a52-ad75-2d13cbd0878c"),
                    public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-lf-b5a53044-8e15-450e-a15a-83f146505206"),
                    host=os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com"),
                    debug=os.getenv("LANGFUSE_DEBUG", "false").lower() == "true"
                )
                print("✅ Langfuse 初始化成功")
            except Exception as e:
                print(f"❌ Langfuse 初始化失败: {e}")
                self.enabled = False
                self._langfuse = None
        else:
            print("⚠️ Langfuse trace 已禁用")
    
    def _should_enable_trace(self) -> bool:
        """检查是否应该启用 trace"""
        return os.getenv("ENABLE_LANGFUSE_TRACE", "true").lower() == "true"
    
    @property
    def client(self):
        """获取 Langfuse 客户端"""
        return self._langfuse
    
    def create_trace(self, name: str, **kwargs):
        """创建 trace"""
        if self.enabled and self._langfuse:
            return self._langfuse.trace(name=name, **kwargs)
        return None
    
    def flush(self):
        """刷新所有待发送的 trace 数据"""
        if self.enabled and self._langfuse:
            self._langfuse.flush()


# 全局实例
tracer = LangfuseTracer()


def trace_llm_call(name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
    """
    LLM 调用追踪装饰器（简化版）
    
    Args:
        name: trace 名称，默认使用函数名
        metadata: 额外的元数据
    """
    def decorator(func: Callable) -> Callable:
        if not tracer.enabled:
            return func
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            trace_name = name or f"{func.__module__}.{func.__name__}"
            
            # 创建简单的记录
            start_time = time.time()
            input_data = {
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys()),
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 记录成功
                end_time = time.time()
                if tracer.client:
                    trace = tracer.create_trace(
                        name=trace_name,
                        input=input_data,
                        output={"result_type": type(result).__name__, "success": True},
                        metadata={
                            "duration_seconds": round(end_time - start_time, 3),
                            "status": "success",
                            **(metadata or {})
                        }
                    )
                
                return result
                
            except Exception as e:
                # 记录错误
                end_time = time.time()
                if tracer.client:
                    trace = tracer.create_trace(
                        name=trace_name,
                        input=input_data,
                        output={"error": str(e), "success": False},
                        metadata={
                            "duration_seconds": round(end_time - start_time, 3),
                            "status": "error",
                            "error_type": type(e).__name__,
                            **(metadata or {})
                        }
                    )
                raise
                
        return wrapper
    return decorator


def trace_agent_action(name: Optional[str] = None, agent_type: str = "general"):
    """
    Agent 动作追踪装饰器（简化版）
    
    Args:
        name: 动作名称
        agent_type: Agent 类型（如 "fortune", "weekly", "score"）
    """
    def decorator(func: Callable) -> Callable:
        if not tracer.enabled:
            return func
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            action_name = name or f"{agent_type}_{func.__name__}"
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                
                end_time = time.time()
                if tracer.client:
                    trace = tracer.create_trace(
                        name=action_name,
                        input={"agent_type": agent_type, "action": func.__name__},
                        output={"result_type": type(result).__name__, "success": True},
                        metadata={
                            "duration_seconds": round(end_time - start_time, 3),
                            "status": "success",
                            "agent_type": agent_type
                        }
                    )
                
                return result
                
            except Exception as e:
                end_time = time.time()
                if tracer.client:
                    trace = tracer.create_trace(
                        name=action_name,
                        input={"agent_type": agent_type, "action": func.__name__},
                        output={"error": str(e), "success": False},
                        metadata={
                            "duration_seconds": round(end_time - start_time, 3),
                            "status": "error",
                            "error_type": type(e).__name__,
                            "agent_type": agent_type
                        }
                    )
                raise
                
        return wrapper
    return decorator


def trace_api_call(endpoint: Optional[str] = None):
    """
    API 调用追踪装饰器（简化版）
    
    Args:
        endpoint: API 端点名称
    """
    def decorator(func: Callable) -> Callable:
        if not tracer.enabled:
            return func
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            api_name = endpoint or func.__name__
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                
                end_time = time.time()
                if tracer.client:
                    trace = tracer.create_trace(
                        name=f"api_{api_name}",
                        input={"endpoint": api_name, "type": "api_call"},
                        output={"result_type": type(result).__name__, "success": True},
                        metadata={
                            "duration_seconds": round(end_time - start_time, 3),
                            "status": "success",
                            "endpoint": api_name
                        }
                    )
                
                return result
                
            except Exception as e:
                end_time = time.time()
                if tracer.client:
                    trace = tracer.create_trace(
                        name=f"api_{api_name}",
                        input={"endpoint": api_name, "type": "api_call"},
                        output={"error": str(e), "success": False},
                        metadata={
                            "duration_seconds": round(end_time - start_time, 3),
                            "status": "error",
                            "error_type": type(e).__name__,
                            "endpoint": api_name
                        }
                    )
                raise
                
        return wrapper
    return decorator

# 导出主要接口
__all__ = [
    'tracer',
    'trace_llm_call', 
    'trace_agent_action',
    'trace_api_call'
]