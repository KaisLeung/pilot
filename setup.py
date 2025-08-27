#!/usr/bin/env python3
"""
P.I.L.O.T. 设置脚本
"""

import os
import sys
import json
from pathlib import Path


def setup_pilot():
    """设置P.I.L.O.T.环境"""
    
    print("🚀 P.I.L.O.T. v1.0-MVP 设置向导")
    print("="*50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 创建配置目录
    config_dir = Path.home() / ".pilot"
    config_dir.mkdir(exist_ok=True)
    print(f"✅ 配置目录: {config_dir}")
    
    # 检查OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("\n❌ 未设置OpenAI API密钥")
        print("请设置环境变量:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("或在 ~/.bashrc 或 ~/.zshrc 中添加上述行")
        
        key_input = input("\n是否现在输入API密钥? (y/n): ").lower().strip()
        if key_input == 'y':
            openai_key = input("请输入OpenAI API密钥: ").strip()
            if openai_key:
                # 保存到配置文件
                config_file = config_dir / "config.json"
                config = {}
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                
                if "openai" not in config:
                    config["openai"] = {}
                config["openai"]["api_key"] = openai_key
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print("✅ API密钥已保存到配置文件")
            else:
                print("⚠️ 跳过API密钥设置")
    else:
        print(f"✅ OpenAI API密钥已设置")
    
    # Google Calendar设置提示
    print("\n📅 Google Calendar设置 (可选)")
    print("如需使用Google Calendar集成:")
    print("1. 访问 https://console.cloud.google.com/")
    print("2. 创建项目并启用Calendar API")
    print("3. 创建OAuth 2.0凭据并下载credentials.json")
    print("4. 将credentials.json放到 ~/.pilot/credentials.json")
    
    credentials_file = config_dir / "credentials.json"
    if credentials_file.exists():
        print("✅ Google凭据文件已存在")
    else:
        print("⚠️ 未找到Google凭据文件")
        creds_path = input("如有credentials.json文件，请输入路径 (回车跳过): ").strip()
        if creds_path and Path(creds_path).exists():
            import shutil
            shutil.copy2(creds_path, credentials_file)
            print("✅ Google凭据文件已复制")
    
    # 创建导出目录
    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)
    print(f"✅ 导出目录: {exports_dir.absolute()}")
    
    print("\n🎉 设置完成!")
    print("\n使用示例:")
    print("  python pilot.py --help")
    print("  python pilot.py --date 2025-01-20 --meetings 13:30-14:00")
    print("  python pilot.py --mode study --cycles 4")


if __name__ == "__main__":
    setup_pilot()