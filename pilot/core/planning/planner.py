"""
LLM驱动的计划生成器
"""

import json
import re
from typing import Optional
from datetime import datetime, time

from ...interfaces.planner import PlannerInterface
from ...interfaces.llm import LLMInterface
from ..models.plan import PlanInput, PlanOutput, Task, TimeSlot, TimeBlock, PomodoroTaskMapping
from ..models.config import PilotConfig


class LLMPlanner(PlannerInterface):
    """LLM驱动的计划生成器"""
    
    def __init__(self, config: PilotConfig, llm: LLMInterface):
        self.config = config
        self.llm = llm
        self.system_prompt = config.get_system_prompt()
    
    def generate_plan(self, plan_input: PlanInput, custom_tasks: str = None) -> Optional[PlanOutput]:
        """生成计划"""
        if not self.validate_input(plan_input):
            return None
        
        try:
            user_prompt = self._build_user_prompt(plan_input, custom_tasks)
            
            # 计算可用时间
            work_start = datetime.combine(plan_input.date, plan_input.work_window_start)
            work_end = datetime.combine(plan_input.date, plan_input.work_window_end)
            total_minutes = int((work_end - work_start).total_seconds() / 60)
            meeting_minutes = sum(meeting.duration_minutes() for meeting in plan_input.meetings)
            available_minutes = total_minutes - meeting_minutes
            
            # 调用LLM API
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.llm.chat_completion(
                messages=messages,
                model=self.config.openai.effective_model,
                max_tokens=self.config.openai.effective_max_tokens,
                temperature=self.config.openai.effective_temperature,
                response_format={"type": "json_object"}
            )
            
            if not response:
                print("❌ LLM调用失败")
                return None
            
            # 解析响应
            plan_data = self._parse_json_response(response)
            
            if plan_data:
                # 后处理：确保任务时间分配符合权重比例
                plan_data = self._adjust_task_time_by_weight(plan_data, available_minutes)
                return self._convert_to_plan_output(plan_data)
            else:
                print(f"❌ JSON解析失败，原始响应：\n{response}")
                return None
                
        except Exception as e:
            print(f"❌ 计划生成失败: {str(e)}")
            return None
    
    def validate_input(self, plan_input: PlanInput) -> bool:
        """验证输入参数"""
        if plan_input.work_window_start >= plan_input.work_window_end:
            print("❌ 工作时间窗口无效")
            return False
        
        # 验证会议时间不冲突
        for i, meeting in enumerate(plan_input.meetings):
            if meeting.start >= meeting.end:
                print(f"❌ 会议{i+1}时间无效")
                return False
        
        return True
    
    def _build_user_prompt(self, plan_input: PlanInput, custom_tasks: str = None) -> str:
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
        
        # 构建任务内容
        tasks_text = ""
        if custom_tasks:
            tasks_text = f"今日具体任务:\n{custom_tasks}\n\n"
        
        prompt = f"""请为以下工作日生成时间规划：

日期: {plan_input.date.strftime('%Y年%m月%d日')}
工作时间: {plan_input.work_window_start.strftime('%H:%M')} - {plan_input.work_window_end.strftime('%H:%M')}
{meetings_text}可用时间: {available_minutes}分钟
模式: {'工作模式' if plan_input.mode == 'work' else '学习模式'}

重要时间规则:
- 午休时间: 12:00-14:00 为固定午休时间，不安排任何工作
- 下午工作: 14:10 开始恢复工作安排

任务时间分配规则:
- 总工作时间按8小时(480分钟)计算，实际可用时间为去除会议和午休后的时间
- 根据任务重要性和复杂度分配权重(1-10分)，重点任务权重8-10，普通任务5-7，轻量任务3-5
- 任务时间 = (任务权重 / 所有任务权重总和) × 总可用时间
- 高权重任务应获得更多时间分配，确保重点工作得到充分时间

{tasks_text}请根据以上任务生成工作计划，按照权重比例分配时间，不要固定每个任务50分钟。重点任务应该获得更多时间，轻量任务时间相对较少。

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
            
            # 处理能量等级的英文到中文映射
            energy_mapping = {
                'High': '高',
                'Medium': '中', 
                'Low': '低'
            }
            energy_value = task_data.get('energy', '中')
            if energy_value in energy_mapping:
                energy_value = energy_mapping[energy_value]
            
            task = Task(
                title=task_data['title'],
                est_min=task_data['est_min'],
                energy=energy_value,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                type=task_data.get('type', 'normal'),
                weight=task_data.get('weight', 5),
                subtasks=task_data.get('subtasks', [])
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
        
        # 解析pomodoro_task_mapping
        pomodoro_mappings = []
        for mapping_data in plan_data.get('pomodoro_task_mapping', []):
            mapping = PomodoroTaskMapping(
                pomodoro_number=mapping_data['pomodoro_number'],
                task_title=mapping_data['task_title'],
                subtask=mapping_data['subtask'],
                focus_content=mapping_data['focus_content']
            )
            pomodoro_mappings.append(mapping)
        
        return PlanOutput(
            capacity_min=plan_data.get('capacity_min', 0),
            meetings=meetings,
            top_tasks=tasks,
            time_blocks=time_blocks,
            pomodoro_task_mapping=pomodoro_mappings,
            risks=plan_data.get('risks', [])
        )
    
    def _adjust_task_time_by_weight(self, plan_data: dict, available_minutes: int) -> dict:
        """根据权重调整任务时间分配"""
        tasks = plan_data.get('top_tasks', [])
        if not tasks:
            return plan_data
        
        # 确保所有任务都有权重，如果没有则根据类型设置默认权重
        for task in tasks:
            if 'weight' not in task or task['weight'] == 0:
                task_type = task.get('type', 'normal')
                if task_type == 'deep':
                    task['weight'] = 8  # 深度任务高权重
                elif task_type == 'normal':
                    task['weight'] = 6  # 常规任务中等权重
                elif task_type == 'light':
                    task['weight'] = 4  # 轻量任务低权重
                else:
                    task['weight'] = 5  # 默认权重
        
        # 计算权重总和
        total_weight = sum(task['weight'] for task in tasks)
        if total_weight == 0:
            return plan_data
        
        # 预留一些缓冲时间(10%)用于任务间隙和意外情况
        effective_work_time = int(available_minutes * 0.9)
        
        # 根据权重比例分配时间
        for task in tasks:
            weight_ratio = task['weight'] / total_weight
            allocated_time = int(effective_work_time * weight_ratio)
            
            # 确保任务时间至少25分钟，最多150分钟
            allocated_time = max(25, min(150, allocated_time))
            task['est_min'] = allocated_time
        
        # 重新计算时间块，确保时间分配一致
        plan_data['top_tasks'] = tasks
        
        print(f"🔄 任务时间已按权重重新分配:")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task['title']}: {task['est_min']}分钟 (权重: {task['weight']})")
        
        return plan_data
