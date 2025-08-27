"""
ICS日历文件生成和管理
"""

import os
import platform
import subprocess
from datetime import datetime, date, time, timedelta
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from icalendar import Calendar, Event, Alarm
import pytz

from ...interfaces.calendar import CalendarInterface
from ...core.models.config import PilotConfig
from ...core.models.schedule import ScheduleItem, CalendarEvent, PomodoroType


class ICSCalendarManager(CalendarInterface):
    """ICS日历文件管理器"""
    
    def __init__(self, config: PilotConfig):
        self.config = config
        self.timezone = pytz.timezone(config.timezone)
    
    def export_schedule(self, target_date: date, schedule: List[ScheduleItem]) -> str:
        """导出日程到ICS文件"""
        return self.export_to_ics_with_reminders(target_date, schedule)
    
    def import_schedule(self, target_date: date, schedule: List[ScheduleItem]) -> bool:
        """导入日程到日历（自动打开ICS文件）"""
        try:
            ics_path = self.export_to_ics_with_reminders(target_date, schedule)
            return self.auto_open_ics_file(ics_path)
        except Exception as e:
            print(f"❌ ICS日历导入失败: {str(e)}")
            return False
    
    def create_events(self, target_date: date, schedule: List[ScheduleItem]) -> bool:
        """创建日历事件（生成ICS文件）"""
        try:
            ics_path = self.export_to_ics_with_reminders(target_date, schedule)
            return self.auto_open_ics_file(ics_path)
        except Exception as e:
            print(f"❌ ICS日历创建失败: {str(e)}")
            return False
    
    def export_to_ics_with_reminders(self, target_date: date, schedule: List[ScheduleItem]) -> str:
        """导出为带提醒的ICS文件"""
        
        try:
            # 创建导出目录
            exports_dir = Path(self.config.exports.ics_dir)
            exports_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            filename = f"pilot_schedule_{target_date.strftime('%Y%m%d')}.ics"
            filepath = exports_dir / filename
            
            # 创建日历对象
            cal = Calendar()
            cal.add('prodid', '-//P.I.L.O.T. v1.0-MVP//pilot.ai//')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            cal.add('x-wr-calname', f'🍅 P.I.L.O.T. 番茄钟计划 - {target_date.strftime("%Y-%m-%d")}')
            cal.add('x-wr-timezone', self.config.timezone)
            cal.add('x-wr-caldesc', 'P.I.L.O.T. 智能时间规划与番茄钟管理')
            
            # 添加每个计划项
            for item in schedule:
                event = self._create_ical_event(target_date, item)
                cal.add_component(event)
            
            # 写入文件
            with open(filepath, 'wb') as f:
                f.write(cal.to_ical())
            
            print(f"📄 ICS文件已生成: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ ICS文件生成失败: {str(e)}")
            raise
    
    def _create_ical_event(self, target_date: date, item: ScheduleItem) -> Event:
        """创建单个iCal事件"""
        event = Event()
        
        # 创建datetime对象
        start_datetime = datetime.combine(target_date, item.start_time)
        end_datetime = datetime.combine(target_date, item.end_time)
        
        # 转换为带时区的datetime
        start_datetime = self.timezone.localize(start_datetime)
        end_datetime = self.timezone.localize(end_datetime)
        
        # 基本事件信息
        event.add('uid', str(uuid4()))
        event.add('summary', self._get_event_summary(item))
        event.add('description', self._get_event_description(item))
        event.add('dtstart', start_datetime)
        event.add('dtend', end_datetime)
        event.add('dtstamp', datetime.now(self.timezone))
        event.add('created', datetime.now(self.timezone))
        event.add('last-modified', datetime.now(self.timezone))
        
        # 分类和标签
        event.add('categories', ['P.I.L.O.T.', '番茄钟', item.type.value])
        event.add('x-pilot-version', '1.0-MVP')
        event.add('x-pilot-type', item.type.value)
        
        # 添加提醒
        alarms = self._get_ics_alarms_for_event(item)
        for alarm in alarms:
            event.add_component(alarm)
        
        return event
    
    def _get_event_summary(self, item: ScheduleItem) -> str:
        """获取事件标题"""
        emoji_map = {
            PomodoroType.FOCUS: "🍅",
            PomodoroType.SHORT_BREAK: "☕",
            PomodoroType.LONG_BREAK: "🛋️",
            PomodoroType.LUNCH: "🍽️",
            PomodoroType.TASK: "📋"
        }
        
        emoji = emoji_map.get(item.type, "📅")
        
        if item.type == PomodoroType.FOCUS:
            cycle_num = getattr(item, 'cycle_number', 1)
            if item.task_title and item.subtask:
                return f"{emoji} 番茄钟 #{cycle_num}: {item.subtask}"
            else:
                return f"{emoji} 番茄钟 #{cycle_num} - 专注时间"
        elif item.type == PomodoroType.SHORT_BREAK:
            return f"{emoji} 番茄休息"
        elif item.type == PomodoroType.LONG_BREAK:
            return f"{emoji} 长休息"
        elif item.type == PomodoroType.LUNCH:
            return f"{emoji} 午休时间"
        elif item.type == PomodoroType.TASK:
            return f"{emoji} {item.title}"
        else:
            return f"{emoji} {item.title}"
    
    def _get_event_description(self, item: ScheduleItem) -> str:
        """获取事件描述"""
        descriptions = []
        
        if item.type == PomodoroType.FOCUS:
            descriptions.extend([
                "🎯 专注工作时间",
                f"⏱️ 持续时间: {item.duration_minutes()}分钟",
                ""
            ])
            
            # 添加任务相关信息
            if item.task_title:
                descriptions.extend([
                    "📋 本次番茄钟任务:",
                    f"主任务: {item.task_title}",
                ])
                
                if item.subtask and item.subtask != item.task_title:
                    descriptions.append(f"具体内容: {item.subtask}")
                
                if item.focus_content:
                    descriptions.extend([
                        "",
                        "🎯 专注要点:",
                        item.focus_content,
                    ])
                
                descriptions.append("")
            
            descriptions.extend([
                "💡 专注提示:",
                "• 关闭通知和干扰源",
                "• 专注于当前任务",
                "• 保持深度工作状态",
                "• 遇到干扰记录后继续"
            ])
            
        elif item.type == PomodoroType.SHORT_BREAK:
            descriptions.extend([
                "☕ 短休息时间",
                f"⏱️ 持续时间: {item.duration_minutes()}分钟",
                "",
                "💡 建议活动:",
                "• 喝水或伸展身体",
                "• 眺望远方放松眼睛",
                "• 做简单的运动",
                "• 避免查看手机或电脑"
            ])
            
        elif item.type == PomodoroType.LONG_BREAK:
            descriptions.extend([
                "🛋️ 长休息时间",
                f"⏱️ 持续时间: {item.duration_minutes()}分钟",
                "",
                "💡 建议活动:",
                "• 散步或户外活动",
                "• 吃点心补充能量",
                "• 与同事聊天放松",
                "• 回顾前面的工作成果"
            ])
            
        elif item.type == PomodoroType.LUNCH:
            descriptions.extend([
                "🍽️ 午餐休息时间",
                "⏱️ 建议用餐并适当休息",
                "🕐 14:10 准备恢复工作",
                "",
                "💡 午休建议:",
                "• 营养均衡的午餐",
                "• 适当的休息或小憩",
                "• 为下午工作做准备"
            ])
            
        elif item.type == PomodoroType.TASK:
            descriptions.extend([
                f"📋 任务: {item.title}",
                f"⏱️ 预计用时: {item.duration_minutes()}分钟"
            ])
            
            if item.focus_content:
                descriptions.extend([
                    "",
                    "📝 任务详情:",
                    item.focus_content
                ])
        
        descriptions.extend([
            "",
            "---",
            "📱 由 P.I.L.O.T. v1.0-MVP 生成",
            "🔗 智能时间规划与番茄钟管理工具"
        ])
        
        return "\n".join(descriptions)
    
    def _get_ics_alarms_for_event(self, item: ScheduleItem) -> List[Alarm]:
        """为事件创建提醒"""
        alarms = []
        
        if item.type == PomodoroType.FOCUS:
            # 番茄钟开始前5分钟和1分钟提醒
            alarms.extend([
                self._create_alarm(timedelta(minutes=-5), "🍅 番茄钟即将开始（5分钟后）"),
                self._create_alarm(timedelta(minutes=-1), "🍅 番茄钟即将开始（1分钟后）")
            ])
        elif item.type == PomodoroType.SHORT_BREAK:
            # 休息结束前1分钟提醒
            alarms.append(
                self._create_alarm(timedelta(minutes=-1), "☕ 番茄休息即将结束，准备继续工作")
            )
        elif item.type == PomodoroType.LONG_BREAK:
            # 长休息结束前5分钟提醒
            alarms.append(
                self._create_alarm(timedelta(minutes=-5), "🛋️ 长休息即将结束，准备恢复工作")
            )
        elif item.type == PomodoroType.TASK:
            # 任务开始前10分钟提醒
            alarms.append(
                self._create_alarm(timedelta(minutes=-10), f"📋 任务即将开始: {item.title}")
            )
        elif item.type == PomodoroType.LUNCH:
            # 午休开始提醒
            alarms.append(
                self._create_alarm(timedelta(minutes=0), "🍽️ 午餐时间，记得14:10恢复工作")
            )
        
        return alarms
    
    def _create_alarm(self, trigger: timedelta, description: str) -> Alarm:
        """创建提醒对象"""
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', description)
        alarm.add('trigger', trigger)
        return alarm
    
    def auto_open_ics_file(self, ics_path: str) -> bool:
        """自动打开ICS文件"""
        try:
            system = platform.system().lower()
            
            if system == 'darwin':  # macOS
                # 使用 'open' 命令打开文件，会自动使用默认的日历应用
                subprocess.run(['open', ics_path], check=True)
                print("📱 正在打开日历应用...")
                print("🎯 请在弹出的日历应用中:")
                print("  1. 选择要添加到的日历")
                print("  2. 点击'添加'或'导入'")
                print("  3. 番茄钟提醒将自动设置")
                return True
                
            elif system == 'windows':
                # Windows使用 'start' 命令
                subprocess.run(['start', ics_path], check=True, shell=True)
                print("📱 正在打开日历应用...")
                return True
                
            elif system == 'linux':
                # Linux使用 'xdg-open' 命令
                subprocess.run(['xdg-open', ics_path], check=True)
                print("📱 正在打开日历应用...")
                return True
            else:
                print(f"⚠️ 不支持的操作系统: {system}")
                return False
                
        except subprocess.CalledProcessError:
            print("❌ 无法自动打开日历应用")
            return False
        except FileNotFoundError:
            print("❌ 找不到系统打开命令")
            return False
        except Exception as e:
            print(f"❌ 打开日历应用时出错: {str(e)}")
            return False
    
    def validate_connection(self) -> bool:
        """验证连接（对于ICS文件，总是返回True）"""
        return True
