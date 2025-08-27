"""
配置管理工具
"""

import os
import json
import click
from pathlib import Path
from typing import Dict, Any, Optional
from ..core.models.config import PilotConfig


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".pilot" / "config.json"
        self.config = None
    
    def load_config(self) -> PilotConfig:
        """加载配置"""
        if self.config is None:
            self.config = PilotConfig.load_from_file(self.config_path)
        return self.config
    
    def save_config(self, config: PilotConfig):
        """保存配置"""
        config.save_to_file(self.config_path)
        self.config = config
    
    def get_openai_config(self) -> Dict[str, Any]:
        """获取OpenAI配置（包含环境变量优先级）"""
        config = self.load_config()
        return {
            "api_key": config.openai.effective_api_key,
            "base_url": config.openai.effective_base_url,
            "model": config.openai.effective_model,
            "max_tokens": config.openai.effective_max_tokens,
            "temperature": config.openai.effective_temperature
        }
    
    def update_openai_config(self, **kwargs):
        """更新OpenAI配置"""
        config = self.load_config()
        
        for key, value in kwargs.items():
            if hasattr(config.openai, key) and value is not None:
                setattr(config.openai, key, value)
        
        self.save_config(config)
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.update_openai_config(api_key=api_key)
    
    def set_base_url(self, base_url: str):
        """设置Base URL"""
        self.update_openai_config(base_url=base_url)
    
    def set_model(self, model: str):
        """设置模型"""
        self.update_openai_config(model=model)
    
    def show_config(self):
        """显示当前配置"""
        config = self.load_config()
        
        click.echo("🔧 当前配置:")
        click.echo("-" * 50)
        
        # OpenAI配置
        click.echo("📡 OpenAI配置:")
        openai_config = self.get_openai_config()
        for key, value in openai_config.items():
            if key == "api_key" and value:
                # 隐藏API密钥的敏感部分
                display_value = f"{value}"
            else:
                display_value = value
            click.echo(f"  {key}: {display_value}")
        
        # 其他配置
        click.echo(f"\n🌏 时区: {config.timezone}")
        click.echo(f"🍅 番茄钟配置:")
        click.echo(f"  工作模式: {config.pomodoro.work_focus_min}分钟专注 + {config.pomodoro.work_break_min}分钟休息")
        click.echo(f"  学习模式: {config.pomodoro.study_focus_min}分钟专注 + {config.pomodoro.study_break_min}分钟休息")
        click.echo(f"📁 导出目录: {config.exports.ics_dir}")
    
    def interactive_setup(self):
        """交互式配置设置"""
        click.echo("🚀 P.I.L.O.T. 交互式配置")
        click.echo("=" * 50)
        
        config = self.load_config()
        
        # API密钥配置
        current_key = config.openai.api_key
        if current_key:
            click.echo(f"当前API密钥: {current_key[:10]}...")
            if click.confirm("是否更新API密钥?"):
                api_key = click.prompt("请输入新的API密钥", hide_input=True)
                config.openai.api_key = api_key
        else:
            api_key = click.prompt("请输入OpenAI API密钥", hide_input=True)
            config.openai.api_key = api_key
        
        # Base URL配置
        base_url = click.prompt("Base URL", default=config.openai.base_url)
        config.openai.base_url = base_url
        
        # 模型配置
        model_choices = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-5"]
        click.echo("可用模型: " + ", ".join(model_choices))
        model = click.prompt("选择模型", default=config.openai.model)
        config.openai.model = model
        
        # 高级配置 (可选)
        if click.confirm("是否配置高级参数? (max_tokens, temperature)"):
            max_tokens = click.prompt("Max Tokens", default=config.openai.max_tokens, type=int)
            temperature = click.prompt("Temperature (0.0-1.0)", default=config.openai.temperature, type=float)
            config.openai.max_tokens = max_tokens
            config.openai.temperature = temperature
        
        # 保存配置
        self.save_config(config)
        click.echo("✅ 配置已保存!")
        
        return config


def get_config_manager() -> ConfigManager:
    """获取配置管理器实例"""
    return ConfigManager()
