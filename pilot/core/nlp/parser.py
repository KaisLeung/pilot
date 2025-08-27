"""
命令解析器
"""

from datetime import datetime
from typing import Optional, Dict, Any

from ...interfaces.llm import LLMInterface


class CommandParser:
    """自然语言命令解析器"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
    
    def parse_command(self, user_input: str) -> Optional[Dict[str, Any]]:
        """解析用户自然语言输入"""
        parsed_data = self.llm.parse_command(user_input)
        
        if parsed_data:
            return self._convert_to_cli_params(parsed_data)
        return None
    
    def _convert_to_cli_params(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """将解析结果转换为CLI参数格式"""
        params = {}
        
        # 处理日期
        date_value = parsed_data.get('date')
        if date_value == 'TODAY' or not date_value:
            params['date'] = datetime.now().strftime('%Y-%m-%d')
        else:
            params['date'] = date_value
        
        # 处理其他参数
        if parsed_data.get('work_window'):
            params['work_window'] = parsed_data['work_window']
        
        if parsed_data.get('meetings'):
            params['meetings'] = parsed_data['meetings']
        
        if parsed_data.get('mode'):
            params['mode'] = parsed_data['mode']
        
        if parsed_data.get('cycles'):
            params['cycles'] = parsed_data['cycles']
        
        if parsed_data.get('pomodoro_start'):
            params['pomodoro_start'] = parsed_data['pomodoro_start']
        
        if parsed_data.get('calendar'):
            params['calendar'] = parsed_data['calendar']
        else:
            params['calendar'] = 'none'
        
        if parsed_data.get('dry_run'):
            params['dry_run'] = parsed_data['dry_run']
        
        # 添加额外信息
        params['command_type'] = parsed_data.get('command_type', 'plan')
        params['task_content'] = parsed_data.get('task_content', '')
        params['focus_tasks'] = parsed_data.get('focus_tasks', [])
        params['inbox_content'] = parsed_data.get('inbox_content', '')
        params['confidence'] = parsed_data.get('confidence', 0.0)
        
        return params
