"""
日历接口定义
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List
from ..core.models.schedule import ScheduleItem


class CalendarInterface(ABC):
    """日历集成抽象接口"""
    
    @abstractmethod
    def export_schedule(self, target_date: date, schedule: List[ScheduleItem]) -> str:
        """导出日程到日历
        
        Args:
            target_date: 目标日期
            schedule: 日程安排列表
            
        Returns:
            导出结果路径或ID
        """
        pass
    
    @abstractmethod
    def import_schedule(self, target_date: date, schedule: List[ScheduleItem]) -> bool:
        """导入日程到日历
        
        Args:
            target_date: 目标日期
            schedule: 日程安排列表
            
        Returns:
            导入是否成功
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """验证日历连接
        
        Returns:
            连接是否有效
        """
        pass
