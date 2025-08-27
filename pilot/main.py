"""
P.I.L.O.T. 主入口模块
"""

import click
from .ui.cli.commands import create_cli


def main():
    """主入口函数"""
    cli = create_cli()
    cli()


if __name__ == '__main__':
    main()
