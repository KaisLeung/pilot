"""
配置相关的CLI命令
"""

import click
from ...utils.config_manager import get_config_manager


@click.group()
def config():
    """配置管理命令"""
    pass


@config.command()
def show():
    """显示当前配置"""
    manager = get_config_manager()
    manager.show_config()


@config.command()
def setup():
    """交互式配置设置"""
    manager = get_config_manager()
    manager.interactive_setup()


@config.command()
@click.option("--api-key", help="设置OpenAI API密钥")
@click.option("--base-url", help="设置OpenAI Base URL")
@click.option("--model", help="设置OpenAI模型")
@click.option("--max-tokens", type=int, help="设置最大Token数")
@click.option("--temperature", type=float, help="设置Temperature参数")
def set(**kwargs):
    """设置配置参数"""
    manager = get_config_manager()
    
    # 过滤掉None值
    updates = {k.replace("-", "_"): v for k, v in kwargs.items() if v is not None}
    
    if not updates:
        click.echo("❌ 请提供至少一个配置参数")
        return
    
    manager.update_openai_config(**updates)
    click.echo("✅ 配置已更新!")
    manager.show_config()


@config.command()
@click.argument("key")
def get(key):
    """获取配置值"""
    manager = get_config_manager()
    config_dict = manager.get_openai_config()
    
    if key in config_dict:
        value = config_dict[key]
        if key == "api_key" and value:
            # 隐藏API密钥
            value = f"{value[:10]}..." if len(value) > 10 else "***"
        click.echo(f"{key}: {value}")
    else:
        click.echo(f"❌ 配置项 '{key}' 不存在")
        click.echo("可用配置项: " + ", ".join(config_dict.keys()))


@config.command()
def env():
    """显示环境变量配置示例"""
    click.echo("🌍 环境变量配置示例:")
    click.echo("-" * 50)
    click.echo("# 添加到 ~/.zshrc 或 ~/.bashrc:")
    click.echo("")
    click.echo("export OPENAI_API_KEY='your-api-key-here'")
    click.echo("export OPENAI_BASE_URL='https://api.bianxie.ai/v1'")
    click.echo("export OPENAI_MODEL='gpt-3.5-turbo'")
    click.echo("export OPENAI_MAX_TOKENS='2000'")
    click.echo("export OPENAI_TEMPERATURE='0.1'")
    click.echo("")
    click.echo("# 然后运行: source ~/.zshrc")
    click.echo("")
    click.echo("💡 环境变量优先级最高，会覆盖配置文件设置")


if __name__ == "__main__":
    config()
