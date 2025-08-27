"""
OpenAI LLM集成
"""

import json
import re
from typing import Optional, Dict, Any
from openai import OpenAI

from ...interfaces.llm import LLMInterface
from ...core.models.config import PilotConfig


class OpenAILLM(LLMInterface):
    """OpenAI LLM实现"""
    
    def __init__(self, config: PilotConfig):
        self.config = config
        if not config.openai.effective_api_key:
            raise ValueError("未设置OpenAI API密钥")
        
        self.client = OpenAI(
            api_key=config.openai.effective_api_key,
            base_url=config.openai.effective_base_url
        )
    
    def chat_completion(
        self, 
        messages: list,
        model: str = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        **kwargs
    ) -> Optional[str]:
        """聊天补全"""
        try:
            response = self.client.chat.completions.create(
                model=model or self.config.openai.effective_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ OpenAI API调用失败: {str(e)}")
            return None
    
    def parse_command(self, user_input: str) -> Optional[Dict[str, Any]]:
        """解析用户命令"""
        try:
            system_prompt = self._get_command_parser_prompt()
            user_prompt = f"用户输入: {user_input}"
            
            response = self.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            if response:
                return self._parse_json_response(response)
            return None
            
        except Exception as e:
            print(f"❌ 命令解析失败: {str(e)}")
            return None
    
    def validate_api_key(self) -> bool:
        """验证API密钥"""
        try:
            # 发送一个简单的请求来验证API密钥
            response = self.chat_completion(
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return response is not None
        except:
            return False
    
    def _get_command_parser_prompt(self) -> str:
        """获取命令解析提示词"""
        return """你是P.I.L.O.T.的命令解析器，负责将用户的自然语言输入转换为标准化的参数。

支持的命令类型：
1. 生成今日计划 - 解析时间、会议、重点任务
2. 开始番茄钟 - 解析任务、轮数、时长
3. 收集箱处理 - 处理碎片信息
4. 晚间复盘 - 生成回顾报告

解析规则：
- 提取日期信息（如果未明确指定，使用TODAY标识）
- 提取工作时间窗口（默认09:30-18:30）
- 提取会议时间段
- 提取模式（work/study）
- 提取轮数信息
- 提取任务内容和重点任务
- 判断命令类型

输出JSON格式（请使用TODAY作为今天的日期标识）：
```json
{
  "command_type": "plan|pomodoro|inbox|review",
  "date": "TODAY",
  "work_window": "HH:MM-HH:MM",
  "meetings": "HH:MM-HH:MM,HH:MM-HH:MM",
  "mode": "work|study",
  "cycles": 4,
  "pomodoro_start": "HH:MM",
  "calendar": "google|ics|none",
  "dry_run": false,
  "task_content": "详细任务内容",
  "focus_tasks": ["任务A", "任务B"],
  "inbox_content": "收集箱内容",
  "confidence": 0.8
}
```

注意：
- 如果信息不明确，使用合理默认值
- confidence 表示解析置信度 (0-1)
- 只输出JSON，不要其他内容"""
    
    def _parse_json_response(self, content: str) -> Optional[dict]:
        """解析JSON响应"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                    
                return None
            except json.JSONDecodeError:
                return None
