"""
调度器接口定义
"""

from abc import ABC, abstractmethod
from datetime import time
from typing import List
import pytz
from ..core.models.plan import PlanOutput
from ..core.models.schedule import ScheduleItem


class SchedulerInterface(ABC):
    """番茄钟调度器抽象接口"""
    
    @abstractmethod
    def schedule_pomodoros(
        self, 
        plan_output: PlanOutput,
        start_time: time,
        work_window_end: time,
        mode: str,
        cycles: int,
        timezone: pytz.BaseTzInfo
    ) -> List[ScheduleItem]:
        """编排番茄钟
        
        Args:
            plan_output: 计划输出
            start_time: 开始时间
            work_window_end: 工作窗口结束时间
            mode: 工作模式 (work/study)
            cycles: 轮数
            timezone: 时区
            
        Returns:
            调度安排列表
        """
        pass
    
    @abstractmethod
    def validate_schedule(self, schedule: List[ScheduleItem]) -> bool:
        """验证调度安排
        
        Args:
            schedule: 调度安排列表
            
        Returns:
            验证是否通过
        """
        pass
