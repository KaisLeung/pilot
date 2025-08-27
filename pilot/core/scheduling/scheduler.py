"""
番茄钟调度器
"""

from datetime import datetime, date, time, timedelta
from typing import List, Tuple
from ..models.config import PilotConfig
from ..models.plan import PlanOutput, Task, TimeSlot
from ..models.schedule import ScheduleItem, PomodoroType


class PomodoroScheduler:
    """番茄钟调度器"""
    
    def __init__(self, config: PilotConfig):
        self.config = config
    
    def schedule_pomodoros(self, target_date: date, plan_output: PlanOutput) -> List[ScheduleItem]:
        """基于计划输出生成番茄钟时间表"""
        schedule = []
        
        # 获取工作时间窗口（从第一个任务推断）
        if not plan_output.top_tasks:
            return schedule
        
        # 从计划中提取工作窗口
        earliest_start = min(task.scheduled_start for task in plan_output.top_tasks if task.scheduled_start)
        latest_end = max(task.scheduled_end for task in plan_output.top_tasks if task.scheduled_end)
        
        if not earliest_start or not latest_end:
            return schedule
        
        # 获取番茄钟配置
        mode = getattr(plan_output, 'mode', 'work')
        if mode == 'work':
            focus_min = self.config.pomodoro.work_focus_min
            break_min = self.config.pomodoro.work_break_min
            cycles = self.config.pomodoro.work_cycles
        else:
            focus_min = self.config.pomodoro.study_focus_min
            break_min = self.config.pomodoro.study_break_min
            cycles = 4  # 学习模式默认4轮
        
        # 获取任务映射（如果LLM提供了的话）
        task_mappings = plan_output.pomodoro_task_mapping if hasattr(plan_output, 'pomodoro_task_mapping') else []
        
        # 如果没有任务映射，则按顺序自动分配任务
        if not task_mappings:
            task_mappings = self._auto_generate_task_mappings(plan_output.top_tasks, cycles)
        
        # 生成番茄钟时间表
        current_time = earliest_start
        cycle_count = 0
        task_mapping_index = 0
        
        while current_time < latest_end and cycle_count < cycles:
            # 检查是否在午休时间
            if self._is_lunch_time(current_time):
                # 添加午休时间
                lunch_start = time(12, 0)
                lunch_end = time(14, 0)
                
                if current_time <= lunch_start:
                    schedule.append(ScheduleItem(
                        title="午休时间",
                        start_time=lunch_start,
                        end_time=lunch_end,
                        type=PomodoroType.LUNCH
                    ))
                    current_time = time(14, 10)  # 14:10恢复工作
                    continue
                else:
                    current_time = time(14, 10)
                    continue
            
            # 添加番茄钟
            cycle_count += 1
            focus_end = self._add_minutes(current_time, focus_min)
            
            # 获取对应的任务信息
            task_info = self._get_task_info_for_cycle(cycle_count, task_mappings)
            
            schedule.append(ScheduleItem(
                title=f"番茄钟 #{cycle_count}",
                start_time=current_time,
                end_time=focus_end,
                type=PomodoroType.FOCUS,
                task_title=task_info['task_title'],
                subtask=task_info['subtask'],
                focus_content=task_info['focus_content'],
                cycle_number=cycle_count
            ))
            
            current_time = focus_end
            
            # 添加休息时间（除了最后一轮）
            if cycle_count < cycles:
                if cycle_count % 4 == 0:  # 每4轮一个长休息
                    break_duration = 15
                    break_type = PomodoroType.LONG_BREAK
                    break_title = "长休息"
                else:
                    break_duration = break_min
                    break_type = PomodoroType.SHORT_BREAK
                    break_title = "短休息"
                
                break_end = self._add_minutes(current_time, break_duration)
                
                schedule.append(ScheduleItem(
                    title=break_title,
                    start_time=current_time,
                    end_time=break_end,
                    type=break_type
                ))
                
                current_time = break_end
        
        # 按时间排序
        schedule.sort(key=lambda x: x.start_time)
        
        return schedule
    
    def _is_lunch_time(self, current_time: time) -> bool:
        """检查是否在午休时间"""
        lunch_start = time(12, 0)
        lunch_end = time(14, 0)
        return lunch_start <= current_time < lunch_end
    
    def _add_minutes(self, base_time: time, minutes: int) -> time:
        """为时间对象添加分钟"""
        dt = datetime.combine(date.today(), base_time)
        dt += timedelta(minutes=minutes)
        return dt.time()
    
    def _get_free_time_slots(self, work_start: time, work_end: time, meetings: List[TimeSlot]) -> List[Tuple[time, time]]:
        """获取空闲时间段"""
        slots = []
        
        # 添加午休时间到会议列表
        lunch_break = TimeSlot(start=time(12, 0), end=time(14, 0))
        all_meetings = meetings + [lunch_break]
        
        # 按开始时间排序
        all_meetings.sort(key=lambda x: x.start)
        
        current_time = work_start
        
        for meeting in all_meetings:
            if current_time < meeting.start:
                slots.append((current_time, meeting.start))
            current_time = max(current_time, meeting.end)
        
        # 添加最后一个时间段
        if current_time < work_end:
            slots.append((current_time, work_end))
        
        return slots
    
    def _auto_generate_task_mappings(self, tasks: List[Task], cycles: int) -> List[dict]:
        """自动生成任务映射"""
        from ..models.plan import PomodoroTaskMapping
        
        mappings = []
        
        # 保持任务原有顺序，不重新排序，因为用户已指定重点顺序
        # 计算每个任务需要的番茄钟数量（每个番茄钟50分钟）
        task_pomodoro_allocation = []
        for task in tasks:
            # 根据任务预计时间计算需要的番茄钟数量
            pomodoro_count = max(1, round(task.est_min / 50))
            task_pomodoro_allocation.append({
                'task': task,
                'pomodoro_count': pomodoro_count,
                'remaining_count': pomodoro_count
            })
        
        current_task_index = 0
        current_task_pomodoro = 1
        
        for cycle in range(1, cycles + 1):
            if current_task_index < len(task_pomodoro_allocation):
                task_info = task_pomodoro_allocation[current_task_index]
                current_task = task_info['task']
                
                # 根据任务时长和当前番茄钟生成子任务描述
                if task_info['pomodoro_count'] == 1:
                    # 单个番茄钟的任务
                    subtask = current_task.title
                    focus_content = f"完成整个任务：{current_task.title}"
                elif task_info['pomodoro_count'] == 2:
                    # 两个番茄钟的任务
                    if current_task_pomodoro == 1:
                        subtask = f"{current_task.title} - 第一阶段"
                        focus_content = f"开始{current_task.title}的前半部分工作"
                    else:
                        subtask = f"{current_task.title} - 第二阶段"
                        focus_content = f"完成{current_task.title}的后半部分工作"
                else:
                    # 多个番茄钟的任务
                    subtask = f"{current_task.title} - 第{current_task_pomodoro}部分"
                    focus_content = f"专注完成{current_task.title}的第{current_task_pomodoro}部分内容"
                
                # 处理子任务列表
                if current_task.subtasks and len(current_task.subtasks) > 0:
                    # 如果有预定义的子任务，按番茄钟顺序分配
                    subtask_index = min(current_task_pomodoro - 1, len(current_task.subtasks) - 1)
                    subtask = current_task.subtasks[subtask_index]
                    focus_content = f"专注于：{subtask}"
                
                mappings.append({
                    'pomodoro_number': cycle,
                    'task_title': current_task.title,
                    'subtask': subtask,
                    'focus_content': focus_content
                })
                
                # 更新计数器
                task_info['remaining_count'] -= 1
                current_task_pomodoro += 1
                
                # 如果当前任务的番茄钟已用完，移到下一个任务
                if task_info['remaining_count'] <= 0:
                    current_task_index += 1
                    current_task_pomodoro = 1
                    
            else:
                # 所有主要任务都分配完了，使用剩余时间进行复习和优化
                mappings.append({
                    'pomodoro_number': cycle,
                    'task_title': "任务复习与优化",
                    'subtask': "回顾和完善已完成的工作",
                    'focus_content': "检查工作质量，优化细节，处理遗留问题"
                })
        
        return mappings
    
    def _get_task_info_for_cycle(self, cycle_number: int, task_mappings: List) -> dict:
        """获取指定番茄钟循环的任务信息"""
        # 查找对应的任务映射
        for mapping in task_mappings:
            # 处理dict和PomodoroTaskMapping对象两种情况
            if isinstance(mapping, dict):
                if mapping.get('pomodoro_number') == cycle_number:
                    return {
                        'task_title': mapping.get('task_title', ''),
                        'subtask': mapping.get('subtask', ''),
                        'focus_content': mapping.get('focus_content', '')
                    }
            else:
                # PomodoroTaskMapping对象
                if hasattr(mapping, 'pomodoro_number') and mapping.pomodoro_number == cycle_number:
                    return {
                        'task_title': mapping.task_title,
                        'subtask': mapping.subtask,
                        'focus_content': mapping.focus_content
                    }
        
        # 如果没找到，返回默认值
        return {
            'task_title': '默认任务',
            'subtask': '继续工作',
            'focus_content': '专注于当前工作'
        }
