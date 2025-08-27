"""
配置管理模块
"""

import os
import json
from pathlib import Path
from typing import Optional


class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".pilot"
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        self.credentials_file = self.config_dir / "credentials.json"
        self.token_file = self.config_dir / "token.json"
        
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        else:
            self._config = self._get_default_config()
            self._save_config()
    
    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            "version": "1.0.0-mvp",
            "timezone": "Asia/Shanghai",
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "model": "gpt-4",
                "max_tokens": 2000,
                "temperature": 0.1
            },
            "google_calendar": {
                "calendar_id": "primary",
                "scopes": [
                    "https://www.googleapis.com/auth/calendar"
                ]
            },
            "pomodoro": {
                "work_focus_min": 50,
                "work_break_min": 10,
                "work_cycles": 6,
                "study_focus_min": 45,
                "study_break_min": 15
            },
            "exports": {
                "ics_dir": "exports"
            }
        }
    
    def _save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    @property
    def openai_api_key(self) -> str:
        """OpenAI API密钥"""
        # 优先从环境变量获取
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            return env_key
        return self._config.get("openai", {}).get("api_key", "")
    
    @property
    def openai_model(self) -> str:
        """OpenAI模型"""
        return self._config.get("openai", {}).get("model", "gpt-4")
    
    @property
    def openai_max_tokens(self) -> int:
        """OpenAI最大token数"""
        return self._config.get("openai", {}).get("max_tokens", 2000)
    
    @property
    def openai_temperature(self) -> float:
        """OpenAI温度参数"""
        return self._config.get("openai", {}).get("temperature", 0.1)
    
    @property
    def timezone(self) -> str:
        """时区"""
        return self._config.get("timezone", "Asia/Shanghai")
    
    @property
    def google_calendar_id(self) -> str:
        """Google日历ID"""
        return self._config.get("google_calendar", {}).get("calendar_id", "primary")
    
    @property
    def google_scopes(self) -> list:
        """Google API权限范围"""
        return self._config.get("google_calendar", {}).get("scopes", [
            "https://www.googleapis.com/auth/calendar"
        ])
    
    @property
    def google_credentials_file(self) -> Path:
        """Google凭据文件路径"""
        return self.credentials_file
    
    @property
    def google_token_file(self) -> Path:
        """Google token文件路径"""
        return self.token_file
    
    @property
    def work_focus_min(self) -> int:
        """工作番茄专注时长"""
        return self._config.get("pomodoro", {}).get("work_focus_min", 50)
    
    @property
    def work_break_min(self) -> int:
        """工作番茄休息时长"""
        return self._config.get("pomodoro", {}).get("work_break_min", 10)
    
    @property
    def work_cycles(self) -> int:
        """工作番茄轮数"""
        return self._config.get("pomodoro", {}).get("work_cycles", 6)
    
    @property
    def study_focus_min(self) -> int:
        """学习番茄专注时长"""
        return self._config.get("pomodoro", {}).get("study_focus_min", 45)
    
    @property
    def study_break_min(self) -> int:
        """学习番茄休息时长"""
        return self._config.get("pomodoro", {}).get("study_break_min", 15)
    
    @property
    def exports_dir(self) -> str:
        """导出目录"""
        return self._config.get("exports", {}).get("ics_dir", "exports")
    
    def set_openai_api_key(self, api_key: str):
        """设置OpenAI API密钥"""
        if "openai" not in self._config:
            self._config["openai"] = {}
        self._config["openai"]["api_key"] = api_key
        self._save_config()
    
    def setup_google_credentials(self, credentials_path: str):
        """设置Google凭据文件"""
        import shutil
        if Path(credentials_path).exists():
            shutil.copy2(credentials_path, self.credentials_file)
            return True
        return False
    
    def has_openai_key(self) -> bool:
        """检查是否有OpenAI API密钥"""
        return bool(self.openai_api_key)
    
    def has_google_credentials(self) -> bool:
        """检查是否有Google凭据"""
        return self.credentials_file.exists()
    
    def get_system_prompt(self) -> str:
        """获取系统提示词 v1.0 MVP版本"""
        return """你是P.I.L.O.T. (Personal Intelligent Life Organization Tool) v1.0-MVP，一个专业的时间管理助手。

核心职责：
1. 根据用户的工作时间窗口和已有会议，生成今日工作计划
2. 将任务拆解为适合番茄钟技术的时间块（≤50分钟）
3. 输出结构化JSON，供后续番茄钟编排使用

时间管理原则：
- 深度工作优先安排在上午或精力最佳时段
- 避开会议时间，合理分配任务
- 单个任务不超过50分钟，复杂任务需拆解
- 考虑能量管理：高中低能量任务合理搭配

输出要求：
严格按照以下JSON Schema输出，不要添加任何额外内容：

```json
{
  "capacity_min": 可用工作容量（分钟数），
  "meetings": [{"start": "HH:MM", "end": "HH:MM"}],
  "top_tasks": [
    {
      "title": "任务标题",
      "est_min": 预计耗时分钟数（≤50），
      "energy": "高|中|低",
      "scheduled_start": "HH:MM",
      "scheduled_end": "HH:MM", 
      "type": "deep|normal|light"
    }
  ],
  "time_blocks": [
    {
      "start": "HH:MM",
      "end": "HH:MM", 
      "label": "时间块描述"
    }
  ],
  "risks": ["风险提示1", "风险提示2"]
}
```

时区：Asia/Shanghai
今天是中国工作日，请生成适合的工作计划。"""