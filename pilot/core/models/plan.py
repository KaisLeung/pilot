"""
计划相关数据模型
"""

from datetime import date, time, datetime, timedelta
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


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
    energy: Literal["高", "中", "低", "High", "Medium", "Low"] = Field(description="能量等级")
    scheduled_start: Optional[time] = None
    scheduled_end: Optional[time] = None
    type: Literal["deep", "normal", "light"] = Field(default="normal", description="任务类型")
    weight: int = Field(default=5, description="任务权重（1-10，数值越大优先级越高）")
    subtasks: List[str] = Field(default_factory=list, description="子任务列表")


class TimeBlock(BaseModel):
    """时间块"""
    start: time
    end: time
    label: str


class PomodoroTaskMapping(BaseModel):
    """番茄钟任务映射"""
    pomodoro_number: int = Field(description="番茄钟编号")
    task_title: str = Field(description="主任务标题")
    subtask: str = Field(description="具体子任务或完整任务")
    focus_content: str = Field(description="专注内容详细描述")


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
    pomodoro_task_mapping: List[PomodoroTaskMapping] = Field(default_factory=list, description="番茄钟任务映射")
    risks: List[str] = Field(default_factory=list)
