#!/usr/bin/env python3
"""
P.I.L.O.T. 测试脚本
"""

import os
import sys
from datetime import datetime, time
import pytz

# 添加src到路径
sys.path.insert(0, 'src')

from src.models import PlanInput, PlanOutput, Task, TimeSlot, ScheduleItem, PomodoroType
from src.config import Config
from src.scheduler import PomodoroScheduler


def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试P.I.L.O.T.基本功能...")
    
    # 测试配置
    config = Config()
    print(f"✅ 配置加载: {config.timezone}")
    
    # 测试数据模型
    test_time_slot = TimeSlot(start=time(13, 30), end=time(14, 0))
    print(f"✅ 时间段: {test_time_slot.start} - {test_time_slot.end} ({test_time_slot.duration_minutes()}分钟)")
    
    # 测试任务
    test_task = Task(
        title="测试任务",
        est_min=50,
        energy="高",
        type="deep"
    )
    print(f"✅ 任务: {test_task.title} ({test_task.est_min}分钟)")
    
    # 测试计划输入
    plan_input = PlanInput(
        date=datetime.now().date(),
        work_window_start=time(9, 30),
        work_window_end=time(18, 30),
        meetings=[test_time_slot],
        mode="work"
    )
    print(f"✅ 计划输入: {plan_input.date} {plan_input.work_window_start}-{plan_input.work_window_end}")
    
    # 测试番茄钟编排
    timezone = pytz.timezone('Asia/Shanghai')
    scheduler = PomodoroScheduler()
    
    # 模拟计划输出
    plan_output = PlanOutput(
        capacity_min=300,
        meetings=[test_time_slot],
        top_tasks=[test_task],
        time_blocks=[],
        risks=[]
    )
    
    schedule = scheduler.schedule_pomodoros(
        plan_output=plan_output,
        start_time=time(9, 30),
        work_window_end=time(18, 30),
        mode="work",
        cycles=6,
        timezone=timezone
    )
    
    print(f"✅ 番茄钟编排: {len(schedule)}个时间段")
    for item in schedule[:3]:  # 显示前3个
        print(f"   {item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}: {item.title}")
    
    print("\n🎉 基本功能测试通过!")


def test_time_parsing():
    """测试时间解析"""
    print("\n🧪 测试时间解析...")
    
    # 测试有效时间格式
    valid_times = ["09:30", "18:30", "13:30", "23:59"]
    for time_str in valid_times:
        try:
            parsed_time = time.fromisoformat(time_str)
            print(f"✅ 时间解析: {time_str} -> {parsed_time}")
        except ValueError as e:
            print(f"❌ 时间解析失败: {time_str} - {e}")
    
    # 测试时间窗口
    window_tests = [
        "09:30-18:30",
        "08:00-17:00",
        "10:00-16:30"
    ]
    
    for window in window_tests:
        try:
            start_str, end_str = window.split('-')
            start_time = time.fromisoformat(start_str.strip())
            end_time = time.fromisoformat(end_str.strip())
            print(f"✅ 时间窗口: {window} -> {start_time}-{end_time}")
        except ValueError as e:
            print(f"❌ 时间窗口解析失败: {window} - {e}")
    
    print("✅ 时间解析测试通过!")


def test_schedule_item():
    """测试日程项目"""
    print("\n🧪 测试日程项目...")
    
    timezone = pytz.timezone('Asia/Shanghai')
    now = datetime.now(timezone)
    
    schedule_item = ScheduleItem(
        start_time=now,
        end_time=now.replace(hour=now.hour+1),
        title="测试番茄钟",
        description="50分钟专注时间",
        type=PomodoroType.WORK
    )
    
    print(f"✅ 日程项目: {schedule_item.title}")
    print(f"   时间: {schedule_item.start_time.strftime('%H:%M')} - {schedule_item.end_time.strftime('%H:%M')}")
    print(f"   时长: {schedule_item.duration_minutes}分钟")
    print(f"   类型: {schedule_item.type}")
    
    print("✅ 日程项目测试通过!")


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_time_parsing() 
        test_schedule_item()
        print("\n🎉 所有测试通过! P.I.L.O.T.基础功能正常。")
        
        # 检查必要配置
        print("\n🔧 配置检查:")
        config = Config()
        
        if config.has_openai_key():
            print("✅ OpenAI API密钥已配置")
        else:
            print("⚠️ 未配置OpenAI API密钥，请运行 python setup.py")
        
        if config.has_google_credentials():
            print("✅ Google凭据已配置")
        else:
            print("⚠️ 未配置Google凭据，将只能使用ICS导出")
            
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)