"""
命令执行器
"""

import click
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional
from .models.config import PilotConfig
from .planning.planner import LLMPlanner
from .scheduling.scheduler import PomodoroScheduler
from ..integrations.llm.openai import OpenAILLM
from ..integrations.calendar.ics_manager import ICSCalendarManager
from .models.plan import PlanInput
from datetime import datetime, time


class CommandExecutor:
    """命令执行器"""
    
    def __init__(self, config: PilotConfig):
        self.config = config
        self.llm = OpenAILLM(config)
        self.planner = LLMPlanner(config, self.llm)
        self.scheduler = PomodoroScheduler(config)
        self.calendar_manager = ICSCalendarManager(config)
    
    def execute_command(self, parsed_params: Dict[str, Any]) -> bool:
        """执行解析后的命令"""
        command_type = parsed_params.get('command_type', 'plan')
        
        try:
            if command_type == 'plan':
                return self._execute_plan_command(parsed_params)
            elif command_type == 'pomodoro':
                return self._execute_pomodoro_command(parsed_params)
            elif command_type == 'inbox':
                return self._execute_inbox_command(parsed_params)
            elif command_type == 'review':
                return self._execute_review_command(parsed_params)
            else:
                click.echo(f"❌ 不支持的命令类型: {command_type}")
                return False
        except Exception as e:
            click.echo(f"❌ 执行失败: {str(e)}")
            return False
    
    def _execute_plan_command(self, params: Dict[str, Any]) -> bool:
        """执行计划命令"""
        click.echo("🧠 正在生成智能计划...")
        
        # 构建计划输入
        plan_input = self._build_plan_input(params)
        target_date = plan_input.date
        
        # 生成计划
        plan_result = self.planner.generate_plan(plan_input, params.get('task_content'))
        
        if not plan_result:
            click.echo("❌ 计划生成失败")
            return False
        
        # 显示计划
        self._display_plan(plan_result)
        
        # 询问是否创建日历
        if self._prompt_calendar_choice():
            calendar_type = self._get_calendar_type()
            self._create_calendar(target_date, plan_result, calendar_type)
        
        return True
    
    def _execute_pomodoro_command(self, params: Dict[str, Any]) -> bool:
        """执行番茄钟命令"""
        click.echo("🍅 启动番茄钟模式...")
        # TODO: 实现番茄钟执行逻辑
        click.echo("⚠️ 番茄钟功能正在开发中")
        return True
    
    def _execute_inbox_command(self, params: Dict[str, Any]) -> bool:
        """执行收集箱命令"""
        click.echo("📥 处理收集箱内容...")
        # TODO: 实现收集箱处理逻辑
        click.echo("⚠️ 收集箱功能正在开发中")
        return True
    
    def _execute_review_command(self, params: Dict[str, Any]) -> bool:
        """执行复盘命令"""
        click.echo("🌙 开始晚间复盘...")
        # TODO: 实现复盘逻辑
        click.echo("⚠️ 复盘功能正在开发中")
        return True
    
    def _build_plan_input(self, params: Dict[str, Any]) -> PlanInput:
        """构建计划输入"""
        # 处理日期
        date_str = params.get('date', 'TODAY')
        if date_str == 'TODAY':
            target_date = datetime.now().date()
        else:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 处理工作时间窗口
        work_window = params.get('work_window', '09:30-18:30')
        start_time_str, end_time_str = work_window.split('-')
        start_time = time.fromisoformat(start_time_str)
        end_time = time.fromisoformat(end_time_str)
        
        # 处理会议
        meetings = []
        meetings_str = params.get('meetings', '')
        if meetings_str:
            from .models.plan import TimeSlot
            for meeting in meetings_str.split(','):
                meeting = meeting.strip()
                if '-' in meeting:
                    meeting_start_str, meeting_end_str = meeting.split('-')
                    meeting_start = time.fromisoformat(meeting_start_str.strip())
                    meeting_end = time.fromisoformat(meeting_end_str.strip())
                    meetings.append(TimeSlot(start=meeting_start, end=meeting_end))
        
        return PlanInput(
            date=target_date,
            work_window_start=start_time,
            work_window_end=end_time,
            meetings=meetings,
            mode=params.get('mode', 'work'),
            cycles=params.get('cycles', 6),
            dry_run=params.get('dry_run', False)
        )
    
    def _display_plan(self, plan_result):
        """显示计划结果"""
        click.echo("\n" + "="*50)
        click.echo("📋 今日计划预览")
        click.echo("="*50)
        
        # 显示重点任务
        if hasattr(plan_result, 'top_tasks') and plan_result.top_tasks:
            click.echo("\n🎯 重点任务:")
            for i, task in enumerate(plan_result.top_tasks[:3], 1):
                energy_emoji = {"高": "🔥", "中": "⚡", "低": "🌙"}.get(task.energy, "⚡")
                start_time = task.scheduled_start.strftime('%H:%M') if task.scheduled_start else '待定'
                end_time = task.scheduled_end.strftime('%H:%M') if task.scheduled_end else '待定'
                click.echo(f"{i}. {task.title} ({task.est_min}分钟) {energy_emoji}")
                click.echo(f"   时间: {start_time}-{end_time}")
        
        # 显示时间块
        if hasattr(plan_result, 'time_blocks') and plan_result.time_blocks:
            click.echo("\n⏰ 时间块:")
            for block in plan_result.time_blocks:
                click.echo(f"{block.start.strftime('%H:%M')}-{block.end.strftime('%H:%M')}: {block.label}")
        
        # 显示可用容量
        if hasattr(plan_result, 'capacity_min'):
            click.echo(f"\n📊 可用时间: {plan_result.capacity_min}分钟")
        
        # 显示风险提示
        if hasattr(plan_result, 'risks') and plan_result.risks:
            click.echo("\n⚠️ 风险提示:")
            for risk in plan_result.risks:
                click.echo(f"• {risk}")
        
        click.echo("\n🎉 P.I.L.O.T. 计划生成完成!")
    
    def _prompt_calendar_choice(self) -> bool:
        """询问是否创建日历"""
        click.echo("\n📅 日历集成")
        return click.confirm("是否创建番茄钟日历?")
    
    def _get_calendar_type(self) -> str:
        """获取日历类型选择"""
        click.echo("请选择日历类型:")
        click.echo("1. Google Calendar")
        click.echo("2. iOS/Mac 日历 (自动打开日历应用)")
        click.echo("3. 生成ICS文件")
        
        choice = click.prompt("请输入选择 (1/2/3)", type=int, default=3)
        
        if choice == 1:
            return 'google'
        elif choice == 2:
            return 'ios'
        else:
            return 'ics'
    
    def _create_calendar(self, target_date: date, plan_result, calendar_type: str):
        """创建日历"""
        try:
            # 生成番茄钟时间表
            schedule = self.scheduler.schedule_pomodoros(target_date, plan_result)
            
            if not schedule:
                click.echo("❌ 无法生成番茄钟时间表")
                return
            
            if calendar_type == 'google':
                click.echo("📅 创建Google Calendar...")
                click.echo("⚠️ Google Calendar集成正在开发中")
                # 降级到ICS文件
                calendar_type = 'ics'
            
            if calendar_type in ['ios', 'ics']:
                click.echo("📅 生成ICS日历文件...")
                
                # 生成ICS文件
                ics_path = self.calendar_manager.export_to_ics_with_reminders(target_date, schedule)
                
                if calendar_type == 'ios':
                    # iOS/Mac自动打开
                    success = self.calendar_manager.auto_open_ics_file(ics_path)
                    if success:
                        click.echo("✅ 日历已自动打开，请在日历应用中确认导入")
                    else:
                        click.echo("⚠️ 无法自动打开，请手动双击ICS文件导入")
                        click.echo(f"📄 文件位置: {ics_path}")
                else:
                    # 仅生成ICS文件
                    click.echo(f"✅ ICS文件已生成: {ics_path}")
                    click.echo("📱 请使用支持ICS格式的日历应用打开此文件")
            
            click.echo("\n🎉 番茄钟日历创建完成!")
            click.echo("📅 日历包含完整的番茄钟时间表和提醒")
            
        except Exception as e:
            click.echo(f"❌ 日历创建失败: {str(e)}")
            click.echo("💡 建议检查文件权限或重试")
