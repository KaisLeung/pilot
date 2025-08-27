"""
数据模型定义
"""

from datetime import date, time, datetime, timedelta
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum


class TimeSlot(BaseModel):
    """时间段"""
    start: time
    end: time
    
    def duration_minutes(self) -> int:
        """计算时长（分钟）"""
        start_dt = datetime.combine(date.today(), self.start)
        end_dt = datetime.combine(date.today(), self.end)
        if end_dt < start_dt:  # 跨天情况
            end_dt += timedelta(days=1)
        return int((end_dt - start_dt).total_seconds() / 60)


class Task(BaseModel):
    """任务"""
    title: str
    est_min: int = Field(description="预计耗时（分钟）")
    energy: Literal["高", "中", "低"] = Field(description="能量等级")
    scheduled_start: Optional[time] = None
    scheduled_end: Optional[time] = None
    type: Literal["deep", "normal", "light"] = Field(default="normal", description="任务类型")


class TimeBlock(BaseModel):
    """时间块"""
    start: time
    end: time
    label: str


class PlanInput(BaseModel):
    """计划输入"""
    date: date
    work_window_start: time
    work_window_end: time
    meetings: List[TimeSlot] = Field(default_factory=list)
    mode: Literal["work", "study"] = "work"
    cycles: int = 4


class PlanOutput(BaseModel):
    """LLM计划输出"""
    capacity_min: int = Field(description="可用容量（分钟）")
    meetings: List[TimeSlot] = Field(default_factory=list)
    top_tasks: List[Task] = Field(default_factory=list)
    time_blocks: List[TimeBlock] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


class PomodoroType(str, Enum):
    """番茄钟类型"""
    WORK = "work"
    STUDY = "study"
    BREAK = "break"
    TASK = "task"


class ScheduleItem(BaseModel):
    """日程项目"""
    start_time: datetime
    end_time: datetime
    title: str
    description: str = ""
    type: PomodoroType
    location: str = ""
    
    @property
    def duration_minutes(self) -> int:
        """时长（分钟）"""
        return int((self.end_time - self.start_time).total_seconds() / 60)


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
            PomodoroType.WORK: "[Work]",
            PomodoroType.STUDY: "[Study]", 
            PomodoroType.BREAK: "[Break]",
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