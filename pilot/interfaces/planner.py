"""
计划器接口定义
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..core.models.plan import PlanInput, PlanOutput


class PlannerInterface(ABC):
    """计划生成器抽象接口"""
    
    @abstractmethod
    def generate_plan(self, plan_input: PlanInput, custom_tasks: str = None) -> Optional[PlanOutput]:
        """生成计划
        
        Args:
            plan_input: 计划输入参数
            custom_tasks: 自定义任务描述
            
        Returns:
            生成的计划输出，失败时返回None
        """
        pass
    
    @abstractmethod
    def validate_input(self, plan_input: PlanInput) -> bool:
        """验证输入参数
        
        Args:
            plan_input: 计划输入参数
            
        Returns:
            验证是否通过
        """
        pass
