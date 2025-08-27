"""
P.I.L.O.T. - Personal Intelligent Life Organization Tool

智能个人生活组织工具
"""

__version__ = "1.0.0-mvp"
__author__ = "P.I.L.O.T. Team"
__description__ = "Personal Intelligent Life Organization Tool"

# 导出主要组件
from .main import main
from .core.models.config import PilotConfig
from .core.models.plan import PlanInput, PlanOutput
from .core.models.schedule import ScheduleItem

__all__ = [
    'main',
    'PilotConfig',
    'PlanInput',
    'PlanOutput', 
    'ScheduleItem',
]
