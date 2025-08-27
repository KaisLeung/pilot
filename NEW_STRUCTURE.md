# P.I.L.O.T. 项目重构 - 模块化架构设计

## 🏗️ 新架构设计原则

### 1. 分层架构
- **表示层 (UI)**: 用户交互、命令行界面
- **业务层 (Core)**: 核心业务逻辑
- **集成层 (Integrations)**: 外部服务集成
- **工具层 (Utils)**: 通用工具和帮助函数
- **接口层 (Interfaces)**: 抽象接口定义

### 2. 单一职责原则
- 每个模块只负责一个特定的功能域
- 降低模块间耦合度
- 提高代码复用性

## 📁 新目录结构

```
pilot/
├── pilot/                      # 主包目录
│   ├── __init__.py             # 包初始化
│   ├── main.py                 # 主入口点
│   │
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── planning/           # 计划生成
│   │   │   ├── __init__.py
│   │   │   ├── planner.py      # LLM计划生成器
│   │   │   └── strategy.py     # 计划策略
│   │   ├── scheduling/         # 调度管理
│   │   │   ├── __init__.py
│   │   │   ├── scheduler.py    # 番茄钟调度器
│   │   │   └── time_manager.py # 时间管理
│   │   ├── nlp/               # 自然语言处理
│   │   │   ├── __init__.py
│   │   │   ├── parser.py       # 命令解析器
│   │   │   └── processor.py    # 语言处理器
│   │   └── models/            # 数据模型
│   │       ├── __init__.py
│   │       ├── plan.py         # 计划相关模型
│   │       ├── schedule.py     # 日程相关模型
│   │       └── config.py       # 配置模型
│   │
│   ├── integrations/          # 外部集成
│   │   ├── __init__.py
│   │   ├── calendar/          # 日历集成
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # 基础接口
│   │   │   ├── google.py       # Google Calendar
│   │   │   └── ics.py          # ICS文件处理
│   │   ├── llm/               # LLM集成
│   │   │   ├── __init__.py
│   │   │   ├── openai.py       # OpenAI集成
│   │   │   └── base.py         # LLM基础接口
│   │   └── notification/      # 通知集成
│   │       ├── __init__.py
│   │       └── system.py       # 系统通知
│   │
│   ├── ui/                    # 用户界面
│   │   ├── __init__.py
│   │   ├── cli/               # 命令行界面
│   │   │   ├── __init__.py
│   │   │   ├── commands.py     # CLI命令定义
│   │   │   ├── prompts.py      # 用户交互提示
│   │   │   └── display.py      # 显示格式化
│   │   └── chat/              # 聊天界面
│   │       ├── __init__.py
│   │       ├── interactive.py  # 交互式聊天
│   │       └── handler.py      # 命令处理
│   │
│   ├── utils/                 # 工具模块
│   │   ├── __init__.py
│   │   ├── time.py            # 时间工具
│   │   ├── file.py            # 文件操作
│   │   ├── format.py          # 格式化工具
│   │   └── system.py          # 系统操作
│   │
│   ├── interfaces/            # 接口定义
│   │   ├── __init__.py
│   │   ├── planner.py         # 计划器接口
│   │   ├── scheduler.py       # 调度器接口
│   │   ├── calendar.py        # 日历接口
│   │   └── llm.py             # LLM接口
│   │
│   └── config/                # 配置管理
│       ├── __init__.py
│       ├── settings.py        # 配置设置
│       └── constants.py       # 常量定义
│
├── tests/                     # 测试目录
│   ├── __init__.py
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   └── fixtures/              # 测试数据
│
├── docs/                      # 文档目录
│   ├── api/                   # API文档
│   ├── user/                  # 用户手册
│   └── dev/                   # 开发文档
│
├── scripts/                   # 脚本目录
│   ├── setup.py              # 安装脚本
│   └── build.py              # 构建脚本
│
├── requirements.txt           # 依赖文件
├── pyproject.toml            # 项目配置
└── README.md                 # 项目说明
```

## 🎯 模块职责划分

### Core 模块 (核心业务)
- **planning/**: 智能计划生成、任务分解
- **scheduling/**: 番茄钟调度、时间管理
- **nlp/**: 自然语言理解、命令解析
- **models/**: 数据结构定义

### Integrations 模块 (外部集成)
- **calendar/**: 日历服务集成 (Google, ICS)
- **llm/**: 大语言模型集成 (OpenAI, 其他)
- **notification/**: 系统通知集成

### UI 模块 (用户界面)
- **cli/**: 命令行界面
- **chat/**: 聊天交互界面

### Utils 模块 (工具库)
- **time.py**: 时间处理工具
- **file.py**: 文件操作工具
- **format.py**: 格式化工具
- **system.py**: 系统操作工具

### Interfaces 模块 (接口定义)
- 定义各模块间的抽象接口
- 支持依赖注入和模块替换
- 提高测试性

## 🚀 重构收益

### 1. 可维护性
- 模块化设计，便于定位和修改
- 清晰的职责划分
- 降低代码复杂度

### 2. 可扩展性
- 插件化架构，易于添加新功能
- 接口驱动，支持多种实现
- 配置化管理

### 3. 可测试性
- 单元测试覆盖
- 依赖注入支持
- Mock测试友好

### 4. 可复用性
- 独立的工具模块
- 标准化的接口
- 组件化设计

## 📋 迁移步骤

1. ✅ 创建新目录结构
2. 🔄 迁移核心业务逻辑
3. 🔄 重构外部集成模块
4. 🔄 重构用户界面模块
5. 🔄 创建工具模块
6. 🔄 定义抽象接口
7. 🔄 更新导入路径
8. 🔄 重构主入口
9. 🔄 更新测试和文档

这个重构将为 P.I.L.O.T. 项目带来更好的架构设计和开发体验！
