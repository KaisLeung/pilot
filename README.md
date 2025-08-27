# P.I.L.O.T. Terminal MVP

**Personal Intelligent Life Organization Tool** - 从计划到日历的自动化闭环

## 🚀 功能特性

- **智能计划生成**: 基于LLM生成今日工作计划和任务拆解
- **番茄钟编排**: 自动编排工作番茄钟(50/10×6)或学习番茄钟(45/15×N)  
- **日历集成**: 支持Google Calendar导入或ICS文件导出
- **会议避让**: 自动避开已有会议时间
- **时间管理**: 基于能量管理的任务安排

## 📦 安装

```bash
# 克隆项目
git clone <repository-url>
cd pilot-terminal

# 安装依赖
pip install -r requirements.txt

# 运行设置向导
python setup.py
```

## ⚙️ 配置

### OpenAI API密钥

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Google Calendar (可选)

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用Calendar API
3. 创建OAuth 2.0凭据并下载`credentials.json`
4. 将文件放到 `~/.pilot/credentials.json`

## 🎯 使用方法

### 基本使用

```bash
# 生成今日计划
python pilot.py

# 指定日期和会议
python pilot.py --date 2025-01-20 --meetings 13:30-14:00,15:30-16:00

# 学习模式
python pilot.py --mode study --cycles 4
```

### 完整参数

```bash
python pilot.py \
  --date 2025-01-20 \
  --work-window 09:30-18:30 \
  --meetings 13:30-14:00,15:30-16:00 \
  --mode work \
  --cycles 6 \
  --pomodoro-start 09:30 \
  --calendar google \
  --dry-run
```

### 参数说明

- `--date`: 目标日期 (YYYY-MM-DD)，默认今天
- `--work-window`: 工作时间窗口 (HH:MM-HH:MM)，默认09:30-18:30
- `--meetings`: 会议时间，逗号分隔 (HH:MM-HH:MM,...)
- `--mode`: 模式选择
  - `work`: 工作模式 (50分钟专注 + 10分钟休息 × 6轮)
  - `study`: 学习模式 (45分钟专注 + 15分钟休息 × N轮)
- `--cycles`: 学习模式轮数 (默认4)
- `--pomodoro-start`: 番茄钟起始时间，默认为工作窗口开始
- `--calendar`: 日历输出方式
  - `google`: Google Calendar
  - `ics`: ICS文件导出
  - `none`: 仅显示计划
- `--dry-run`: 预览模式，不实际导入日历

## 📋 示例输出

```
🚀 P.I.L.O.T. v1.0-MVP 启动
📅 日期: 2025-01-20
⏰ 工作时间: 09:30 - 18:30
🍅 模式: work (50/10×6)
📋 会议: 13:30-14:00

🧠 正在生成智能计划...
✅ 计划生成完成

🍅 正在编排番茄钟...
✅ 成功编排 6 个番茄钟

==================================================
📋 今日计划预览
==================================================

🎯 重点任务:
  1. 项目架构设计 (50分钟) 🔥
  2. 代码重构 (45分钟) ⚡
  3. 文档更新 (30分钟) 🌙

🍅 番茄钟安排:
  09:30 - 10:20: 🍅 番茄钟 #1
  10:20 - 10:30: ☕ 番茄休息
  10:30 - 11:20: 🍅 番茄钟 #2
  ...

📅 正在导入GOOGLE日历...
✅ Google Calendar 导入成功

🎉 P.I.L.O.T. 执行完成! 祝您今日高效!
```

## 🗂 项目结构

```
pilot-terminal/
├── pilot.py              # 主入口
├── setup.py              # 设置向导
├── requirements.txt      # 依赖列表
├── src/
│   ├── config.py         # 配置管理
│   ├── models.py         # 数据模型
│   ├── planner.py        # LLM计划生成
│   ├── scheduler.py      # 番茄钟编排
│   └── calendar_manager.py # 日历管理
└── exports/              # ICS文件导出目录
```

## 🔧 故障排除

### OpenAI API调用失败
- 检查API密钥是否正确设置
- 确认账户有足够余额
- 检查网络连接

### Google Calendar导入失败
- 确认credentials.json文件存在
- 检查是否已启用Calendar API
- 首次使用需要浏览器授权

### 时间冲突
- 系统会自动避让会议时间
- 如无足够空闲时间，会显示警告
- 可调整工作窗口或减少番茄钟轮数

## 📝 版本信息

- 版本: v1.0.0-MVP
- 时区: Asia/Shanghai
- Python要求: ≥3.8

## 🤝 贡献

欢迎提交Issue和Pull Request来改进P.I.L.O.T.！

## 📄 许可证

MIT License