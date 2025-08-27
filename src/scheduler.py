"""
番茄钟编排模块
"""

from datetime import datetime, time, timedelta
from typing import List, Optional, Tuple
import pytz

from .models import PlanOutput, ScheduleItem, PomodoroType, TimeSlot
from .config import Config


class PomodoroScheduler:
    """番茄钟编排器"""
    
    def __init__(self):
        pass
    
    def schedule_pomodoros(
        self, 
        plan_output: PlanOutput,
        start_time: time,
        work_window_end: time,
        mode: str,
        cycles: int,
        timezone: pytz.BaseTzInfo
    ) -> List[ScheduleItem]:
        """编排番茄钟"""
        
        # 获取今天的日期
        today = datetime.now(timezone).date()
        
        # 转换为datetime
        start_dt = datetime.combine(today, start_time).replace(tzinfo=timezone)
        end_dt = datetime.combine(today, work_window_end).replace(tzinfo=timezone)
        
        # 获取番茄钟参数
        if mode == 'work':
            focus_min = 50
            break_min = 10
            pomodoro_cycles = 6
            pomodoro_type = PomodoroType.WORK
        else:  # study
            focus_min = 45
            break_min = 15
            pomodoro_cycles = cycles
            pomodoro_type = PomodoroType.STUDY
        
        # 获取空闲时间段
        free_slots = self._get_free_time_slots(
            start_dt, end_dt, plan_output.meetings, timezone
        )
        
        # 编排番茄钟
        schedule = []
        current_time = start_dt
        
        for cycle in range(pomodoro_cycles):
            # 安排专注时间
            focus_slot = self._find_next_available_slot(
                current_time, focus_min, free_slots
            )
            
            if not focus_slot:
                print(f"⚠️ 无法安排第{cycle + 1}个番茄钟（{focus_min}分钟）")
                break
            
            # 创建专注时段
            focus_title = f"番茄钟 #{cycle + 1}"
            if mode == 'study':
                focus_title = f"学习番茄钟 #{cycle + 1}"
            
            focus_item = ScheduleItem(
                start_time=focus_slot[0],
                end_time=focus_slot[1],
                title=focus_title,
                description=f"{focus_min}分钟专注时间",
                type=pomodoro_type
            )
            schedule.append(focus_item)
            
            # 更新当前时间
            current_time = focus_slot[1]
            
            # 安排休息时间（除了最后一轮）
            if cycle < pomodoro_cycles - 1:
                break_slot = self._find_next_available_slot(
                    current_time, break_min, free_slots
                )
                
                if break_slot:
                    break_item = ScheduleItem(
                        start_time=break_slot[0],
                        end_time=break_slot[1],
                        title="番茄休息",
                        description=f"{break_min}分钟休息时间",
                        type=PomodoroType.BREAK
                    )
                    schedule.append(break_item)
                    current_time = break_slot[1]
                else:
                    print(f"⚠️ 无法安排第{cycle + 1}个休息时间（{break_min}分钟）")
        
        # 尝试安排重点任务
        self._schedule_tasks(schedule, plan_output.top_tasks, free_slots, timezone)
        
        # 按时间排序
        schedule.sort(key=lambda x: x.start_time)
        
        return schedule
    
    def _get_free_time_slots(
        self, 
        start_dt: datetime, 
        end_dt: datetime, 
        meetings: List[TimeSlot],
        timezone: pytz.BaseTzInfo
    ) -> List[Tuple[datetime, datetime]]:
        """获取空闲时间段"""
        
        # 转换会议时间为datetime
        meeting_periods = []
        today = start_dt.date()
        
        for meeting in meetings:
            meeting_start = datetime.combine(today, meeting.start).replace(tzinfo=timezone)
            meeting_end = datetime.combine(today, meeting.end).replace(tzinfo=timezone)
            meeting_periods.append((meeting_start, meeting_end))
        
        # 排序会议
        meeting_periods.sort(key=lambda x: x[0])
        
        # 计算空闲时段
        free_slots = []
        current_time = start_dt
        
        for meeting_start, meeting_end in meeting_periods:
            # 添加会议前的空闲时间
            if current_time < meeting_start:
                free_slots.append((current_time, meeting_start))
            
            # 更新当前时间到会议结束
            current_time = max(current_time, meeting_end)
        
        # 添加最后的空闲时间
        if current_time < end_dt:
            free_slots.append((current_time, end_dt))
        
        return free_slots
    
    def _find_next_available_slot(
        self, 
        start_time: datetime, 
        duration_min: int, 
        free_slots: List[Tuple[datetime, datetime]]
    ) -> Optional[Tuple[datetime, datetime]]:
        """寻找下一个可用时间段"""
        
        needed_duration = timedelta(minutes=duration_min)
        
        for slot_start, slot_end in free_slots:
            # 如果开始时间在这个空闲段内
            if slot_start <= start_time <= slot_end:
                # 检查从start_time开始是否有足够时间
                if start_time + needed_duration <= slot_end:
                    return (start_time, start_time + needed_duration)
            
            # 如果开始时间早于这个空闲段，检查空闲段是否足够大
            elif start_time < slot_start:
                if slot_end - slot_start >= needed_duration:
                    return (slot_start, slot_start + needed_duration)
        
        return None
    
    def _schedule_tasks(
        self, 
        schedule: List[ScheduleItem], 
        tasks: List,
        free_slots: List[Tuple[datetime, datetime]],
        timezone: pytz.BaseTzInfo
    ):
        """安排重点任务"""
        
        # 获取已占用的时间段
        occupied_slots = [(item.start_time, item.end_time) for item in schedule]
        
        # 计算剩余空闲时间
        remaining_free_slots = self._subtract_occupied_time(free_slots, occupied_slots)
        
        for task in tasks:
            # 尝试安排任务
            task_duration = timedelta(minutes=task.est_min)
            
            # 如果任务已有预定时间，优先使用
            if task.scheduled_start and task.scheduled_end:
                today = datetime.now(timezone).date()
                task_start = datetime.combine(today, task.scheduled_start).replace(tzinfo=timezone)
                task_end = datetime.combine(today, task.scheduled_end).replace(tzinfo=timezone)
                
                # 检查时间是否可用
                if self._is_time_available(task_start, task_end, remaining_free_slots):
                    task_item = ScheduleItem(
                        start_time=task_start,
                        end_time=task_end,
                        title=task.title,
                        description=f"预计{task.est_min}分钟 | 能量需求: {task.energy}",
                        type=PomodoroType.TASK
                    )
                    schedule.append(task_item)
                    
                    # 更新剩余空闲时间
                    remaining_free_slots = self._subtract_occupied_time(
                        remaining_free_slots, [(task_start, task_end)]
                    )
                    continue
            
            # 寻找合适的时间段
            task_slot = None
            for slot_start, slot_end in remaining_free_slots:
                if slot_end - slot_start >= task_duration:
                    task_slot = (slot_start, slot_start + task_duration)
                    break
            
            if task_slot:
                task_item = ScheduleItem(
                    start_time=task_slot[0],
                    end_time=task_slot[1],
                    title=task.title,
                    description=f"预计{task.est_min}分钟 | 能量需求: {task.energy}",
                    type=PomodoroType.TASK
                )
                schedule.append(task_item)
                
                # 更新剩余空闲时间
                remaining_free_slots = self._subtract_occupied_time(
                    remaining_free_slots, [task_slot]
                )
            else:
                print(f"⚠️ 无法安排任务: {task.title} ({task.est_min}分钟)")
    
    def _subtract_occupied_time(
        self, 
        free_slots: List[Tuple[datetime, datetime]], 
        occupied_slots: List[Tuple[datetime, datetime]]
    ) -> List[Tuple[datetime, datetime]]:
        """从空闲时间中减去已占用时间"""
        
        result = []
        
        for free_start, free_end in free_slots:
            current_start = free_start
            
            # 按开始时间排序占用时间
            sorted_occupied = sorted(occupied_slots, key=lambda x: x[0])
            
            for occ_start, occ_end in sorted_occupied:
                # 如果占用时间在当前空闲时间之前，跳过
                if occ_end <= current_start:
                    continue
                
                # 如果占用时间在当前空闲时间之后，结束
                if occ_start >= free_end:
                    break
                
                # 如果有重叠，分割空闲时间
                if occ_start > current_start:
                    result.append((current_start, occ_start))
                
                current_start = max(current_start, occ_end)
            
            # 添加剩余的空闲时间
            if current_start < free_end:
                result.append((current_start, free_end))
        
        return result
    
    def _is_time_available(
        self, 
        start_time: datetime, 
        end_time: datetime, 
        free_slots: List[Tuple[datetime, datetime]]
    ) -> bool:
        """检查时间是否可用"""
        
        for slot_start, slot_end in free_slots:
            if slot_start <= start_time and end_time <= slot_end:
                return True
        
        return False