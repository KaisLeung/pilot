"""
抽象接口定义模块

定义了P.I.L.O.T.系统中各个组件的抽象接口，
支持依赖注入和模块替换。
"""

from .planner import PlannerInterface
from .scheduler import SchedulerInterface
from .calendar import CalendarInterface
from .llm import LLMInterface

__all__ = [
    'PlannerInterface',
    'SchedulerInterface', 
    'CalendarInterface',
    'LLMInterface',
]
