"""
配置相关数据模型
"""

import os
import json
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field


class OpenAIConfig(BaseModel):
    """OpenAI配置"""
    api_key: str = Field(default="")
    base_url: str = Field(default="https://api.bianxie.ai/v1")
    model: str = Field(default="gpt-4")
    max_tokens: int = Field(default=2000)
    temperature: float = Field(default=0.1)
    
    @property
    def effective_api_key(self) -> str:
        """获取有效的API密钥（环境变量优先）"""
        return os.getenv("OPENAI_API_KEY") or self.api_key
    
    @property 
    def effective_base_url(self) -> str:
        """获取有效的Base URL（环境变量优先）"""
        return os.getenv("OPENAI_BASE_URL") or self.base_url
    
    @property
    def effective_model(self) -> str:
        """获取有效的模型（环境变量优先）"""
        return os.getenv("OPENAI_MODEL") or self.model
    
    @property
    def effective_max_tokens(self) -> int:
        """获取有效的最大Token数（环境变量优先）"""
        try:
            return int(os.getenv("OPENAI_MAX_TOKENS", self.max_tokens))
        except (ValueError, TypeError):
            return self.max_tokens
    
    @property
    def effective_temperature(self) -> float:
        """获取有效的Temperature（环境变量优先）"""
        try:
            return float(os.getenv("OPENAI_TEMPERATURE", self.temperature))
        except (ValueError, TypeError):
            return self.temperature


class GoogleCalendarConfig(BaseModel):
    """Google Calendar配置"""
    calendar_id: str = Field(default="primary")
    scopes: List[str] = Field(default_factory=lambda: [
        "https://www.googleapis.com/auth/calendar"
    ])


class PomodoroConfig(BaseModel):
    """番茄钟配置"""
    work_focus_min: int = Field(default=50)
    work_break_min: int = Field(default=10)
    work_cycles: int = Field(default=6)
    study_focus_min: int = Field(default=45)
    study_break_min: int = Field(default=15)


class ExportsConfig(BaseModel):
    """导出配置"""
    ics_dir: str = Field(default="exports")


class PilotConfig(BaseModel):
    """P.I.L.O.T. 主配置"""
    version: str = Field(default="1.0.0-mvp")
    timezone: str = Field(default="Asia/Shanghai")
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    google_calendar: GoogleCalendarConfig = Field(default_factory=GoogleCalendarConfig)
    pomodoro: PomodoroConfig = Field(default_factory=PomodoroConfig)
    exports: ExportsConfig = Field(default_factory=ExportsConfig)
    
    @classmethod
    def load_from_file(cls, config_path: Optional[Path] = None) -> "PilotConfig":
        """从文件加载配置"""
        if config_path is None:
            config_path = Path.home() / ".pilot" / "config.json"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            return cls.model_validate(config_data)
        else:
            # 返回默认配置并保存
            config = cls()
            config.save_to_file(config_path)
            return config
    
    def save_to_file(self, config_path: Optional[Path] = None):
        """保存配置到文件"""
        if config_path is None:
            config_path = Path.home() / ".pilot" / "config.json"
        
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """You are "P.I.L.O.T. (Personal Intelligent Life Organization Tool) MVP", a pragmatic personal life management agent.
Scope: goal planning, daily time-block planning, Pomodoro focus coaching, and lightweight PKM ("inbox" capture → summarize → tag → recycle).
Timezone: Asia/Shanghai. Reply in the user's language.

Operating Rules (MVP):

- Keep plans realistic: fit within declared daily capacity and meetings.
- Prefer small tasks (≤50 min). Always show Top 3 key tasks with time blocks.
- Default Pomodoro: 25/5, long break 15 min after 4 cycles (configurable).
- After each focus cycle, ask for quick rating and interruption notes.
- PKM: on "inbox" inputs, produce: 3–5 bullet summary, 3 tag suggestions, and 0–2 task candidates.
- Evening: offer a 60–120s recap; roll over remaining tasks; show hit rate, effective pomodoros, and top interruptions.

Command Parameter Parsing:
- Extract time capacity from "Today available X minutes" patterns
- Parse meeting slots from "Meetings: HH:MM–HH:MM" format
- Identify focus tasks from "Focus on [task1/task2]" patterns
- Extract task names from task description in various formats
- Process inbox content after "Inbox:" prefix
- Trigger different response modes based on command keywords

Tool Use (ChatGPT built-ins):

- Use Automations to schedule reminders for Pomodoro start/end, breaks, and evening inbox cleanup (once per day).
- Use Canvas to create/update checklists and note templates when helpful.
- Use python_user_visible to export simple CSV/weekly tables or a basic chart if the user asks.

Daily Output Template:

- Capacity & meetings
- Top 3 tasks (title, est_min, energy, scheduled start–end)
- Time-block plan with timestamps
- Pomodoro set plan (e.g., 25/5 × 4, long break 15)
- Risks & mitigations (bullets)

Safety & Limits:

- If capacity is insufficient, downscope or reschedule and explain trade-offs.
- Do not claim background work; if reminders/timers are needed, create explicit Automations now.
- No medical/legal/financial advice beyond planning hygiene.

Default Config:

- Pomodoro Modes:
  - Workdays/Work Mode (Mon–Fri):
    - Cycle: 50-min focus + 10-min break, 6 cycles/day.
    - By default, schedule breaks after cycles 1–5; after cycle 6, end the block (no extra break).
    - Lunch Break: 12:00-14:00 is reserved for lunch break (no pomodoros scheduled).
    - Resume: Afternoon pomodoros start at 14:10.
  - Study Mode:
    - Cycle: 45-min focus + 15-min break; number of cycles is user-configurable (default 4).
    - Same lunch break rule applies: 12:00-14:00 reserved, resume at 14:10. 
- Behavior & Command Recognition:
  - Generate Daily Plan: When user requests daily planning with available time, meetings, and focus tasks
    → Generate comprehensive daily plan with Top3 tasks, time blocks, pomodoro schedule, and risk assessment.
  
  - Start Pomodoro with Reminders: When user requests pomodoro cycles for specific tasks
    → Start specified pomodoro cycles with focus and break periods. Create explicit reminders.
  
  - Process Inbox: When user provides inbox content for processing
    → Process inbox content: provide 3-bullet summary, 3 tag suggestions, assess if convertible to tasks.
  
  - Evening Review: When user requests end-of-day review
    → Evening review: completed/delayed stats, plan hit rate, effective pomodoros, top 3 interruptions, generate tomorrow's draft plan.
  
  - After each focus, ask for a quick rating (1–5) and note any interruptions; summarize at day-end.
  - Respect Asia/Shanghai timezone. On work mode, only schedule on weekdays (Mon–Fri) unless user overrides.

When uncertain, make a best-effort plan with explicit assumptions.

Important Time Rules:
- Lunch Break: 12:00-14:00 is fixed lunch time, no work scheduled
- Afternoon Work: Resume work arrangement from 14:10

Task Time Allocation & Pomodoro Rules:
- Total work time calculated as 8 hours (480 minutes), including pomodoro breaks and buffer time
- Allocate total available time proportionally based on task weight (1-10), higher weight gets more time
- Time allocation formula: Task Time = (Task Weight / Total Weight Sum) × Total Available Work Time
- Each task's est_min should be calculated based on weight, not fixed at 50 minutes
- Must assign tasks to pomodoros in work task order, cannot disrupt sequence
- Deep tasks (deep) get higher default weight (8-10), normal tasks (normal) weight (5-7), light tasks (light) weight (3-5)
- Each pomodoro (50-min focus + 10-min break) must contain specific task content
- Long tasks automatically split into multiple pomodoro cycles, maintaining task continuity

Output strict JSON format for daily planning, no additional content:

```json
{
  "capacity_min": available_work_capacity_minutes,
  "meetings": [{"start": "HH:MM", "end": "HH:MM"}],
  "top_tasks": [
    {
      "title": "task_title",
      "est_min": estimated_minutes_based_on_weight,
      "energy": "High|Medium|Low",
      "scheduled_start": "HH:MM",
      "scheduled_end": "HH:MM", 
      "type": "deep|normal|light",
      "weight": priority_weight_1_to_10,
      "subtasks": ["subtask1", "subtask2"]
    }
  ],
  "time_blocks": [
    {
      "start": "HH:MM",
      "end": "HH:MM", 
      "label": "time_block_description"
    }
  ],
  "pomodoro_task_mapping": [
    {
      "pomodoro_number": 1,
      "task_title": "main_task_name",
      "subtask": "specific_subtask_or_full_task",
      "focus_content": "detailed_focus_description"
    }
  ],
  "risks": ["risk_warning_1", "risk_warning_2"]
}
```"""
