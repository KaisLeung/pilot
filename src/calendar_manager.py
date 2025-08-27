"""
日历管理模块
"""

import os
import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional
import pytz
from icalendar import Calendar, Event
from uuid import uuid4

# Google Calendar相关导入
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from .models import ScheduleItem, CalendarEvent
from .config import Config


class CalendarManager:
    """日历管理器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.timezone = pytz.timezone(config.timezone)
    
    def import_to_google(self, target_date: date, schedule: List[ScheduleItem]) -> bool:
        """导入到Google Calendar"""
        
        if not GOOGLE_AVAILABLE:
            print("❌ Google Calendar依赖未安装，请安装 google-auth 等相关包")
            return False
        
        if not self.config.has_google_credentials():
            print("❌ 未找到Google凭据文件，请先设置credentials.json")
            return False
        
        try:
            # 获取或刷新凭据
            creds = self._get_google_credentials()
            if not creds:
                print("❌ Google授权失败")
                return False
            
            # 构建服务
            service = build('calendar', 'v3', credentials=creds)
            
            # 转换为CalendarEvent
            events = [CalendarEvent.from_schedule_item(item) for item in schedule]
            
            # 批量创建事件
            calendar_id = self.config.google_calendar_id
            created_count = 0
            
            for event in events:
                try:
                    google_event = {
                        'summary': event.summary,
                        'description': event.description,
                        'start': {
                            'dateTime': event.start_datetime.isoformat(),
                            'timeZone': self.config.timezone,
                        },
                        'end': {
                            'dateTime': event.end_datetime.isoformat(), 
                            'timeZone': self.config.timezone,
                        },
                        'location': event.location,
                        'source': {
                            'title': 'P.I.L.O.T.',
                            'url': 'https://github.com/pilot-terminal'
                        }
                    }
                    
                    service.events().insert(
                        calendarId=calendar_id,
                        body=google_event
                    ).execute()
                    
                    created_count += 1
                    
                except Exception as e:
                    print(f"⚠️ 创建事件失败: {event.summary} - {str(e)}")
            
            print(f"✅ 成功创建 {created_count}/{len(events)} 个日历事件")
            return created_count > 0
            
        except Exception as e:
            print(f"❌ Google Calendar导入失败: {str(e)}")
            return False
    
    def export_to_ics(self, target_date: date, schedule: List[ScheduleItem]) -> str:
        """导出为ICS文件"""
        
        try:
            # 创建导出目录
            exports_dir = Path(self.config.exports_dir)
            exports_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            filename = f"{target_date.strftime('%Y%m%d')}_pilot.ics"
            filepath = exports_dir / filename
            
            # 创建日历对象
            cal = Calendar()
            cal.add('prodid', '-//P.I.L.O.T. v1.0-MVP//mxm.dk//')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            cal.add('x-wr-calname', f'P.I.L.O.T. 计划 - {target_date.strftime("%Y-%m-%d")}')
            cal.add('x-wr-timezone', self.config.timezone)
            
            # 转换为CalendarEvent并添加到日历
            for item in schedule:
                event = CalendarEvent.from_schedule_item(item)
                
                ical_event = Event()
                ical_event.add('uid', str(uuid4()))
                ical_event.add('summary', event.summary)
                ical_event.add('description', event.description)
                ical_event.add('dtstart', event.start_datetime)
                ical_event.add('dtend', event.end_datetime)
                ical_event.add('dtstamp', datetime.now(self.timezone))
                ical_event.add('created', datetime.now(self.timezone))
                ical_event.add('last-modified', datetime.now(self.timezone))
                
                if event.location:
                    ical_event.add('location', event.location)
                
                # 添加自定义属性
                ical_event.add('categories', 'P.I.L.O.T.')
                ical_event.add('x-pilot-version', '1.0-MVP')
                ical_event.add('x-pilot-type', item.type.value)
                
                cal.add_component(ical_event)
            
            # 写入文件
            with open(filepath, 'wb') as f:
                f.write(cal.to_ical())
            
            return str(filepath.absolute())
            
        except Exception as e:
            print(f"❌ ICS导出失败: {str(e)}")
            raise
    
    def _get_google_credentials(self) -> Optional[Credentials]:
        """获取Google凭据"""
        
        creds = None
        token_file = self.config.google_token_file
        
        # 加载已保存的凭据
        if token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    str(token_file), 
                    self.config.google_scopes
                )
            except Exception as e:
                print(f"⚠️ 加载token失败: {e}")
        
        # 如果没有有效凭据，进行授权流程
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("✅ Google凭据已刷新")
                except Exception as e:
                    print(f"⚠️ 凭据刷新失败: {e}")
                    creds = None
            
            if not creds:
                # 执行授权流程
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.config.google_credentials_file),
                        self.config.google_scopes
                    )
                    creds = flow.run_local_server(port=0)
                    print("✅ Google授权完成")
                except Exception as e:
                    print(f"❌ Google授权失败: {e}")
                    return None
            
            # 保存凭据
            if creds:
                try:
                    with open(token_file, 'w') as token:
                        token.write(creds.to_json())
                    print("✅ 凭据已保存")
                except Exception as e:
                    print(f"⚠️ 保存凭据失败: {e}")
        
        return creds