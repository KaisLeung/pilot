"""
LLM计划生成模块
"""

import json
import re
from typing import Optional
from openai import OpenAI
from datetime import datetime, time

from .models import PlanInput, PlanOutput, Task, TimeSlot, TimeBlock
from .config import Config


class PlannerLLM:
    """LLM驱动的计划生成器"""
    
    def __init__(self, config: Config):
        self.config = config
        if not config.has_openai_key():
            raise ValueError("未设置OpenAI API密钥，请设置环境变量 OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=config.openai_api_key)
        self.system_prompt = config.get_system_prompt()
    
    def generate_plan(self, plan_input: PlanInput, retry_count: int = 1) -> Optional[PlanOutput]:
        """生成计划"""
        try:
            user_prompt = self._build_user_prompt(plan_input)
            
            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.config.openai_max_tokens,
                temperature=self.config.openai_temperature,
                response_format={"type": "json_object"}
            )
            
            # 解析响应
            content = response.choices[0].message.content.strip()
            plan_data = self._parse_json_response(content)
            
            if plan_data:
                return self._convert_to_plan_output(plan_data)
            else:
                print(f"❌ JSON解析失败，原始响应：\n{content}")
                if retry_count > 0:
                    print(f"🔄 重试中... ({retry_count} 次剩余)")
                    return self.generate_plan(plan_input, retry_count - 1)
                return None
                
        except Exception as e:
            print(f"❌ LLM调用失败: {str(e)}")
            if retry_count > 0:
                print(f"🔄 重试中... ({retry_count} 次剩余)")
                return self.generate_plan(plan_input, retry_count - 1)
            return None
    
    def _build_user_prompt(self, plan_input: PlanInput) -> str:
        """构建用户提示词"""
        # 计算可用容量
        work_start = datetime.combine(plan_input.date, plan_input.work_window_start)
        work_end = datetime.combine(plan_input.date, plan_input.work_window_end)
        total_minutes = int((work_end - work_start).total_seconds() / 60)
        
        # 减去会议时间
        meeting_minutes = sum(meeting.duration_minutes() for meeting in plan_input.meetings)
        available_minutes = total_minutes - meeting_minutes
        
        # 构建会议列表
        meetings_text = ""
        if plan_input.meetings:
            meetings_list = [f"{m.start.strftime('%H:%M')}-{m.end.strftime('%H:%M')}" for m in plan_input.meetings]
            meetings_text = f"已安排会议: {', '.join(meetings_list)}\n"
        
        prompt = f"""请为以下工作日生成时间规划：

日期: {plan_input.date.strftime('%Y年%m月%d日')}
工作时间: {plan_input.work_window_start.strftime('%H:%M')} - {plan_input.work_window_end.strftime('%H:%M')}
{meetings_text}可用时间: {available_minutes}分钟
模式: {'工作模式' if plan_input.mode == 'work' else '学习模式'}

请生成包含3-5个重点任务的工作计划，每个任务≤50分钟。考虑能量管理，合理安排深度工作、常规任务和轻量任务。

输出严格的JSON格式，不要包含任何markdown或其他格式。"""
        
        return prompt
    
    def _parse_json_response(self, content: str) -> Optional[dict]:
        """解析JSON响应"""
        try:
            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                # 尝试提取JSON部分（去除可能的markdown标记）
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                
                # 尝试查找大括号包围的JSON
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                    
                return None
            except json.JSONDecodeError:
                return None
    
    def _convert_to_plan_output(self, plan_data: dict) -> PlanOutput:
        """转换为PlanOutput对象"""
        # 解析tasks
        tasks = []
        for task_data in plan_data.get('top_tasks', []):
            # 解析时间
            scheduled_start = None
            scheduled_end = None
            if task_data.get('scheduled_start'):
                scheduled_start = time.fromisoformat(task_data['scheduled_start'])
            if task_data.get('scheduled_end'):
                scheduled_end = time.fromisoformat(task_data['scheduled_end'])
            
            task = Task(
                title=task_data['title'],
                est_min=task_data['est_min'],
                energy=task_data.get('energy', '中'),
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                type=task_data.get('type', 'normal')
            )
            tasks.append(task)
        
        # 解析meetings
        meetings = []
        for meeting_data in plan_data.get('meetings', []):
            meeting = TimeSlot(
                start=time.fromisoformat(meeting_data['start']),
                end=time.fromisoformat(meeting_data['end'])
            )
            meetings.append(meeting)
        
        # 解析time_blocks
        time_blocks = []
        for block_data in plan_data.get('time_blocks', []):
            block = TimeBlock(
                start=time.fromisoformat(block_data['start']),
                end=time.fromisoformat(block_data['end']),
                label=block_data['label']
            )
            time_blocks.append(block)
        
        return PlanOutput(
            capacity_min=plan_data.get('capacity_min', 0),
            meetings=meetings,
            top_tasks=tasks,
            time_blocks=time_blocks,
            risks=plan_data.get('risks', [])
        )