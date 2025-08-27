"""
LLM接口定义
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class LLMInterface(ABC):
    """大语言模型抽象接口"""
    
    @abstractmethod
    def chat_completion(
        self, 
        messages: list,
        model: str = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        **kwargs
    ) -> Optional[str]:
        """聊天补全
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            响应内容，失败时返回None
        """
        pass
    
    @abstractmethod
    def parse_command(self, user_input: str) -> Optional[Dict[str, Any]]:
        """解析用户命令
        
        Args:
            user_input: 用户输入
            
        Returns:
            解析结果字典，失败时返回None
        """
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """验证API密钥
        
        Returns:
            API密钥是否有效
        """
        pass
