"""
外部集成模块

包含日历、LLM、通知等外部服务集成。
"""

from .llm.openai import OpenAILLM

__all__ = [
    'OpenAILLM',
]
