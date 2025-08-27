#!/usr/bin/env python3
"""
P.I.L.O.T. 快速设置脚本
"""

import click
from pilot.utils.config_manager import get_config_manager


@click.command()
@click.option('--quick', '-q', is_flag=True, help='快速设置模式（仅设置API密钥）')
def setup(quick):
    """P.I.L.O.T. 初始化设置"""
    
    click.echo("🚀 P.I.L.O.T. v1.0-MVP 设置向导")
    click.echo("=" * 50)
    
    manager = get_config_manager()
    
    if quick:
        # 快速设置模式
        click.echo("⚡ 快速设置模式")
        api_key = click.prompt("请输入OpenAI API密钥", hide_input=True)
        manager.set_api_key(api_key)
        click.echo("✅ API密钥已设置！")
    else:
        # 完整交互式设置
        manager.interactive_setup()
    
    click.echo("\n🎉 设置完成！")
    click.echo("\n📋 使用方法:")
    click.echo("  python main.py chat -i              # 交互模式")
    click.echo("  python main.py config show          # 查看配置")
    click.echo("  python main.py config set --help    # 设置配置")
    click.echo("  python main.py config env           # 环境变量示例")
    
    click.echo("\n💡 配置优先级: 环境变量 > 配置文件 > 默认值")


if __name__ == '__main__':
    setup()
