# P.I.L.O.T. - Personal Intelligent Life Organization Tool

🚀 **重构版本 v1.0.0-MVP** - 智能个人生活组织工具

## 🎯 功能特性

- 🧠 **智能计划生成**: 基于LLM的个性化工作计划
- 🍅 **番茄钟管理**: 自动调度和提醒
- 📅 **日历集成**: 支持Google Calendar和ICS导出
- 💬 **自然语言交互**: 直接用中文描述需求
- ⏰ **午休时间管理**: 自动避开12:00-14:00午休
- 🔔 **智能提醒**: 番茄钟开始/结束提醒

## 🏗️ 架构设计

### 模块化架构
```
pilot/
├── core/              # 核心业务逻辑
│   ├── planning/      # 计划生成
│   ├── scheduling/    # 调度管理  
│   ├── nlp/          # 自然语言处理
│   └── models/       # 数据模型
├── integrations/     # 外部集成
│   ├── llm/         # LLM服务
│   ├── calendar/    # 日历服务
│   └── notification/ # 通知服务
├── ui/              # 用户界面
│   ├── cli/         # 命令行界面
│   └── chat/        # 聊天界面
├── utils/           # 工具模块
└── interfaces/      # 抽象接口
```

### 设计原则
- **接口驱动**: 支持依赖注入和模块替换
- **单一职责**: 每个模块专注特定功能
- **类型安全**: 使用Pydantic确保数据结构正确性
- **配置集中**: 统一的配置管理

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化设置
```bash
python setup_new.py
```

### 3. 开始使用

**交互模式:**
```bash
python main.py chat -i
```

**单次命令:**
```bash
python main.py chat "今天可用480分钟，会议：13:30–14:00。重点推进项目A/项目B。"
```

## 💬 使用示例

### 生成今日计划
```
👤 您: 今天的工作任务是：A.完成个人助手agent的开发，B.完成ANR优化验证，C.跟进AI writing需求。重点完成A、B两个任务

🤖 P.I.L.O.T.: [自动解析并生成番茄钟计划]
```

### 收集箱功能
```
👤 您: 收集箱：刚读了一篇关于AI效率工具的文章
🤖 P.I.L.O.T.: [自动提取要点、标签、任务建议]
```

## 📅 日历集成

支持多种日历平台：

1. **📱 iOS/Mac日历**: 自动打开日历应用导入
2. **🌐 Google Calendar**: 在线同步到云端
3. **📄 ICS文件**: 通用格式，支持所有日历应用

### 提醒功能
- 🍅 **番茄钟**: 开始前5分钟+1分钟提醒
- ☕ **休息**: 结束前1分钟提醒
- 📋 **任务**: 开始前10分钟提醒

## ⚙️ 配置

配置文件位置: `~/.pilot/config.json`

### 主要配置项
```json
{
  "openai": {
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-3.5-turbo"
  },
  "pomodoro": {
    "work_focus_min": 50,
    "work_break_min": 10,
    "work_cycles": 6
  }
}
```

## 🔧 开发

### 项目结构
- **可维护性**: 模块化设计，职责清晰
- **可扩展性**: 插件化架构，易于添加新功能
- **可测试性**: 接口抽象，支持单元测试

### 添加新功能
1. 定义接口 (`interfaces/`)
2. 实现核心逻辑 (`core/`)
3. 创建集成模块 (`integrations/`)
4. 更新UI (`ui/`)

## 📋 命令参考

```bash
python main.py chat -i                    # 交互模式
python main.py chat "描述工作需求"         # 单次解析
python main.py version                    # 版本信息
```

## 🆚 重构对比

| 特性 | 重构前 | 重构后 |
|------|--------|--------|
| 架构 | 单体文件 | 模块化分层 |
| 接口 | 硬编码依赖 | 接口驱动 |
| 配置 | 分散管理 | 集中配置 |
| 测试 | 难以测试 | 易于测试 |
| 扩展 | 修改现有代码 | 插件式添加 |

## 🔄 备份说明

旧版本代码已备份到 `.back/` 目录：
- `.back/src/` - 原始源代码
- `.back/pilot.py` - 原始主文件
- `.back/test_pilot.py` - 原始测试文件

## 🎉 开始体验

重构后的P.I.L.O.T.为您提供更强大、更灵活的时间管理能力！

```bash
python main.py chat -i
```

让AI助手帮您规划完美的一天！
