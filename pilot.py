#!/usr/bin/env python3
"""
P.I.L.O.T. Terminal MVP - Personal Intelligent Life Organization Tool
从计划到日历的自动化闭环
"""

import os
import sys
import json
import click
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pytz

from src.planner import PlannerLLM
from src.scheduler import PomodoroScheduler
from src.calendar_manager import CalendarManager
from src.models import PlanInput, PlanOutput
from src.config import Config


@click.command()
@click.option('--date', default=None, help='目标日期 (YYYY-MM-DD)，默认今天')
@click.option('--work-window', default='09:30-18:30', help='工作时间窗口 (HH:MM-HH:MM)')
@click.option('--meetings', default='', help='会议时间，逗号分隔 (HH:MM-HH:MM,HH:MM-HH:MM)')
@click.option('--mode', type=click.Choice(['work', 'study']), default='work', help='模式：work=50/10×6, study=45/15×N')
@click.option('--cycles', default=4, type=int, help='学习模式轮数（默认4）')
@click.option('--pomodoro-start', default=None, help='番茄钟起始时间 (HH:MM)，默认为工作窗口开始')
@click.option('--calendar', type=click.Choice(['google', 'ics', 'none']), default='google', help='日历输出方式')
@click.option('--dry-run', is_flag=True, help='仅预览，不实际导入日历')
@click.version_option(version='1.0.0-mvp')
def main(date, work_window, meetings, mode, cycles, pomodoro_start, calendar, dry_run):
    """P.I.L.O.T. - 智能时间规划与番茄钟管理工具"""
    
    try:
        # 初始化配置
        config = Config()
        timezone = pytz.timezone('Asia/Shanghai')
        
        # 检查必要的配置
        if not config.has_openai_key():
            click.echo("❌ 未设置OpenAI API密钥")
            click.echo("请运行: python setup.py 进行配置")
            sys.exit(1)
        
        # 解析输入参数
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else datetime.now(timezone).date()
        except ValueError:
            click.echo(f"❌ 无效的日期格式: {date}，应为 YYYY-MM-DD")
            sys.exit(1)
        
        try:
            start_time, end_time = parse_time_window(work_window)
        except ValueError as e:
            click.echo(f"❌ {str(e)}")
            sys.exit(1)
            
        try:
            meeting_slots = parse_meetings(meetings) if meetings else []
        except ValueError as e:
            click.echo(f"❌ 会议时间解析失败: {str(e)}")
            sys.exit(1)
        
        try:
            pomodoro_start_time = time.fromisoformat(pomodoro_start) if pomodoro_start else start_time
        except ValueError:
            click.echo(f"❌ 无效的番茄钟开始时间: {pomodoro_start}，应为 HH:MM")
            sys.exit(1)
        
        # 构建计划输入
        plan_input = PlanInput(
            date=target_date,
            work_window_start=start_time,
            work_window_end=end_time,
            meetings=meeting_slots,
            mode=mode,
            cycles=cycles
        )
        
        click.echo(f"🚀 P.I.L.O.T. v1.0-MVP 启动")
        click.echo(f"📅 日期: {target_date}")
        click.echo(f"⏰ 工作时间: {start_time} - {end_time}")
        click.echo(f"🍅 模式: {mode} ({'50/10×6' if mode == 'work' else f'45/15×{cycles}'})")
        if meeting_slots:
            click.echo(f"📋 会议: {', '.join([f'{m.start}-{m.end}' for m in meeting_slots])}")
        
        # 1. 生成计划
        click.echo("\n🧠 正在生成智能计划...")
        planner = PlannerLLM(config)
        plan_output = planner.generate_plan(plan_input)
        
        if not plan_output:
            click.echo("❌ 计划生成失败")
            sys.exit(1)
            
        click.echo("✅ 计划生成完成")
        
        # 2. 编排番茄钟
        click.echo("\n🍅 正在编排番茄钟...")
        scheduler = PomodoroScheduler()
        schedule = scheduler.schedule_pomodoros(
            plan_output=plan_output,
            start_time=pomodoro_start_time,
            work_window_end=end_time,
            mode=mode,
            cycles=cycles,
            timezone=timezone
        )
        
        if not schedule:
            click.echo("❌ 番茄钟编排失败")
            sys.exit(1)
            
        click.echo(f"✅ 成功编排 {len([s for s in schedule if s.type in ['work', 'study']])} 个番茄钟")
        
        # 3. 预览计划
        print_schedule_preview(plan_output, schedule)
        
        if dry_run:
            click.echo("\n🔍 预览模式，未实际导入日历")
            return
            
        # 4. 导入日历
        if calendar != 'none':
            click.echo(f"\n📅 正在导入{calendar.upper()}日历...")
            calendar_manager = CalendarManager(config)
            
            if calendar == 'google':
                success = calendar_manager.import_to_google(target_date, schedule)
                if success:
                    click.echo("✅ Google Calendar 导入成功")
                else:
                    click.echo("⚠️ Google Calendar 导入失败，正在生成ICS文件...")
                    ics_path = calendar_manager.export_to_ics(target_date, schedule)
                    click.echo(f"📄 ICS文件已生成: {ics_path}")
            elif calendar == 'ics':
                ics_path = calendar_manager.export_to_ics(target_date, schedule)
                click.echo(f"✅ ICS文件已生成: {ics_path}")
        
        click.echo(f"\n🎉 P.I.L.O.T. 执行完成! 祝您今日高效!")
        
    except Exception as e:
        click.echo(f"❌ 错误: {str(e)}")
        sys.exit(1)


def parse_time_window(window: str) -> Tuple[time, time]:
    """解析时间窗口 HH:MM-HH:MM"""
    try:
        start_str, end_str = window.split('-')
        start_time = time.fromisoformat(start_str.strip())
        end_time = time.fromisoformat(end_str.strip())
        return start_time, end_time
    except ValueError:
        raise ValueError(f"无效的时间窗口格式: {window}，应为 HH:MM-HH:MM")


def parse_meetings(meetings_str: str) -> List:
    """解析会议时间字符串"""
    from src.models import TimeSlot
    
    meetings = []
    if not meetings_str.strip():
        return meetings
        
    for meeting in meetings_str.split(','):
        meeting = meeting.strip()
        if '-' in meeting:
            start_str, end_str = meeting.split('-')
            start_time = time.fromisoformat(start_str.strip())
            end_time = time.fromisoformat(end_str.strip())
            meetings.append(TimeSlot(start=start_time, end=end_time))
    
    return meetings


def print_schedule_preview(plan_output: PlanOutput, schedule):
    """打印计划预览"""
    click.echo("\n" + "="*50)
    click.echo("📋 今日计划预览")
    click.echo("="*50)
    
    # 任务列表
    if plan_output.top_tasks:
        click.echo("\n🎯 重点任务:")
        for i, task in enumerate(plan_output.top_tasks, 1):
            energy_icon = {"高": "🔥", "中": "⚡", "低": "🌙"}.get(task.energy, "⚡")
            click.echo(f"  {i}. {task.title} ({task.est_min}分钟) {energy_icon}")
    
    # 时间块
    if plan_output.time_blocks:
        click.echo("\n⏰ 时间块:")
        for block in plan_output.time_blocks:
            click.echo(f"  {block.start} - {block.end}: {block.label}")
    
    # 番茄钟计划
    click.echo("\n🍅 番茄钟安排:")
    for item in schedule:
        type_icon = {
            'work': '🍅',
            'study': '📚', 
            'break': '☕',
            'task': '📋'
        }.get(item.type, '📋')
        click.echo(f"  {item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}: {type_icon} {item.title}")
    
    # 风险提示
    if plan_output.risks:
        click.echo("\n⚠️ 风险提示:")
        for risk in plan_output.risks:
            click.echo(f"  • {risk}")


if __name__ == '__main__':
    main()