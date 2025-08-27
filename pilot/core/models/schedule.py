"""
调度相关数据模型
"""

from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class PomodoroType(str, Enum):
    """番茄钟类型"""
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    LUNCH = "lunch"
    TASK = "task"


class ScheduleItem(BaseModel):
    """日程项目"""
    start_time: time
    end_time: time
    title: str
    description: str = ""
    type: PomodoroType
    location: str = ""
    # 新增任务相关字段
    task_title: str = ""  # 关联的主任务标题
    subtask: str = ""  # 具体的子任务或任务内容
    focus_content: str = ""  # 专注内容描述
    cycle_number: int = 0  # 番茄钟循环编号
    
    def duration_minutes(self) -> int:
        """时长（分钟）"""
        start_dt = datetime.combine(datetime.today().date(), self.start_time)
        end_dt = datetime.combine(datetime.today().date(), self.end_time)
        return int((end_dt - start_dt).total_seconds() / 60)


class CalendarEvent(BaseModel):
    """日历事件"""
    summary: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    location: str = ""
    
    @classmethod
    def from_schedule_item(cls, item: ScheduleItem) -> "CalendarEvent":
        """从日程项目创建日历事件"""
        type_prefix = {
            PomodoroType.FOCUS: "[Focus]",
            PomodoroType.SHORT_BREAK: "[Break]", 
            PomodoroType.LONG_BREAK: "[Long Break]",
            PomodoroType.LUNCH: "[Lunch]",
            PomodoroType.TASK: "[Task]"
        }
        
        prefix = type_prefix.get(item.type, "[Task]")
        summary = f"{prefix} {item.title}"
        
        description = f"{item.description}\n\n" if item.description else ""
        description += f"来源: P.I.L.O.T. v1.0-MVP\n"
        description += f"时长: {item.duration_minutes}分钟\n"
        description += f"类型: {item.type.value}"
        
        return cls(
            summary=summary,
            description=description,
            start_datetime=item.start_time,
            end_datetime=item.end_time,
            location=item.location
        )
