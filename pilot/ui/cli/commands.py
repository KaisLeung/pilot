"""
CLI命令定义
"""

import click
from ...core.models.config import PilotConfig
from ...integrations.llm.openai import OpenAILLM
from ...core.nlp.parser import CommandParser
from ...core.executor import CommandExecutor
from .config_commands import config


def create_cli():
    """创建CLI应用"""
    
    @click.group()
    @click.version_option(version='1.0.0-mvp')
    def cli():
        """P.I.L.O.T. - 智能时间规划与番茄钟管理工具"""
        pass

    @cli.command()
    @click.argument('input_text', nargs=-1)
    @click.option('--interactive', '-i', is_flag=True, help='交互模式')
    def chat(input_text, interactive):
        """自然语言交互模式"""
        try:
            # 加载配置
            config = PilotConfig.load_from_file()
            
            # 初始化LLM、解析器和执行器
            llm = OpenAILLM(config)
            parser = CommandParser(llm)
            executor = CommandExecutor(config)
            
            if interactive:
                # 交互模式
                click.echo("🤖 P.I.L.O.T. 自然语言交互模式")
                click.echo("💬 直接输入您的需求，例如：")
                click.echo("   '今天可用480分钟，会议：13:30–14:00。重点推进项目A/项目B。'")
                click.echo("   输入 'quit' 或 'exit' 退出\n")
                
                while True:
                    user_input = input("👤 您: ").strip()
                    if user_input.lower() in ['quit', 'exit', '退出']:
                        click.echo("👋 再见！")
                        break
                    
                    if not user_input:
                        continue
                    
                    # 解析命令
                    click.echo("🧠 正在解析指令...")
                    parsed_params = parser.parse_command(user_input)
                    if parsed_params:
                        click.echo(f"✅ 指令解析完成 (置信度: {parsed_params.get('confidence', 0)*100:.1f}%)")
                        click.echo(f"📋 命令类型: {parsed_params.get('command_type', 'unknown')}")
                        
                        # 执行命令
                        success = executor.execute_command(parsed_params)
                        if not success:
                            click.echo("❌ 命令执行失败，请检查输入或重试")
                    else:
                        click.echo("❌ 无法理解您的指令，请重新输入")
            else:
                # 单次命令模式
                if not input_text:
                    click.echo("❌ 请提供输入文本或使用 -i 进入交互模式")
                    return
                
                user_input = ' '.join(input_text)
                click.echo("🧠 正在解析指令...")
                parsed_params = parser.parse_command(user_input)
                if parsed_params:
                    click.echo(f"✅ 指令解析完成 (置信度: {parsed_params.get('confidence', 0)*100:.1f}%)")
                    click.echo(f"📋 命令类型: {parsed_params.get('command_type', 'unknown')}")
                    
                    # 执行命令
                    success = executor.execute_command(parsed_params)
                    if not success:
                        click.echo("❌ 命令执行失败")
                else:
                    click.echo("❌ 无法理解您的指令")
                    
        except Exception as e:
            click.echo(f"❌ 错误: {str(e)}")

    @cli.command()
    def version():
        """显示版本信息"""
        click.echo("P.I.L.O.T. v1.0.0-mvp")
        click.echo("Personal Intelligent Life Organization Tool")
    
    # 添加配置命令组
    cli.add_command(config)

    return cli
