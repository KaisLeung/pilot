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
        
        # 生成番茄钟时间表
        current_time = earliest_start
        cycle_count = 0
        
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
            
            schedule.append(ScheduleItem(
                title=f"番茄钟 #{cycle_count}",
                start_time=current_time,
                end_time=focus_end,
                type=PomodoroType.FOCUS
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
        
        # 添加具体任务到时间表
        for task in plan_output.top_tasks:
            if task.scheduled_start and task.scheduled_end:
                schedule.append(ScheduleItem(
                    title=task.title,
                    start_time=task.scheduled_start,
                    end_time=task.scheduled_end,
                    type=PomodoroType.TASK
                ))
        
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
