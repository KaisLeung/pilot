# P.I.L.O.T. 配置指南

## 🔧 配置概述

P.I.L.O.T. 支持多种配置方式，优先级从高到低：

1. **环境变量** (最高优先级)
2. **配置文件** (~/.pilot/config.json)
3. **默认值** (最低优先级)

## 🚀 快速开始

### 1. 初始设置

```bash
# 完整交互式设置
python setup.py

# 快速设置（仅设置API密钥）
python setup.py --quick
```

### 2. 使用配置命令

```bash
# 查看当前配置
python main.py config show

# 交互式配置设置
python main.py config setup

# 查看环境变量示例
python main.py config env
```

## ⚙️ 配置方式

### 方式1: 环境变量配置（推荐）

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
export OPENAI_API_KEY='your-api-key-here'
export OPENAI_BASE_URL='https://api.bianxie.ai/v1'
export OPENAI_MODEL='gpt-3.5-turbo'
export OPENAI_MAX_TOKENS='2000'
export OPENAI_TEMPERATURE='0.1'
```

然后运行：
```bash
source ~/.zshrc
```

### 方式2: 命令行设置

```bash
# 设置API密钥
python main.py config set --api-key "your-api-key"

# 设置Base URL
python main.py config set --base-url "https://api.bianxie.ai/v1"

# 设置模型
python main.py config set --model "gpt-4"

# 批量设置
python main.py config set --api-key "key" --base-url "url" --model "model"
```

### 方式3: 配置文件

配置文件位置: `~/.pilot/config.json`

```json
{
  "version": "1.0.0-mvp",
  "timezone": "Asia/Shanghai",
  "openai": {
    "api_key": "your-api-key",
    "base_url": "https://api.bianxie.ai/v1",
    "model": "gpt-3.5-turbo",
    "max_tokens": 2000,
    "temperature": 0.1
  },
  "google_calendar": {
    "calendar_id": "primary",
    "scopes": ["https://www.googleapis.com/auth/calendar"]
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
```

## 🔍 配置查看和管理

```bash
# 查看所有配置
python main.py config show

# 查看特定配置项
python main.py config get api_key
python main.py config get base_url
python main.py config get model
```

## 🌐 支持的API提供商

### 1. 官方OpenAI
```bash
export OPENAI_BASE_URL='https://api.openai.com/v1'
```

### 2. 编写AI（推荐）
```bash
export OPENAI_BASE_URL='https://api.bianxie.ai/v1'
```

### 3. 其他兼容服务
只要兼容OpenAI API格式的服务都可以使用，修改 `OPENAI_BASE_URL` 即可。

## 🔑 API密钥管理

### 安全最佳实践

1. **使用环境变量存储API密钥**（推荐）
2. **不要将API密钥提交到代码仓库**
3. **定期轮换API密钥**
4. **使用最小权限原则**

### 密钥获取

- **OpenAI**: https://platform.openai.com/api-keys
- **编写AI**: 从您的编写AI账户获取

## 🛠️ 高级配置

### 模型选择
```bash
# GPT-3.5 Turbo (推荐，性价比高)
python main.py config set --model "gpt-3.5-turbo"

# GPT-4 (更强但较贵)
python main.py config set --model "gpt-4"

# GPT-4 Turbo
python main.py config set --model "gpt-4-turbo"
```

### 参数调优
```bash
# 增加输出长度
python main.py config set --max-tokens 3000

# 调整创造性（0.0-1.0）
python main.py config set --temperature 0.2
```

## 🔧 故障排除

### 常见问题

1. **API配额超限**
   ```
   Error code: 429 - You exceeded your current quota
   ```
   **解决方案**: 检查API账户余额，或切换到其他API提供商

2. **API密钥无效**
   ```
   Error code: 401 - Invalid API key
   ```
   **解决方案**: 检查API密钥是否正确设置

3. **网络连接错误**
   **解决方案**: 检查网络连接和防火墙设置

### 配置验证

```bash
# 验证当前配置
python main.py config show

# 测试API连接
python main.py chat "测试连接"
```

## 📝 示例配置

### 开发环境
```bash
export OPENAI_BASE_URL='https://api.bianxie.ai/v1'
export OPENAI_MODEL='gpt-3.5-turbo'
export OPENAI_MAX_TOKENS='2000'
export OPENAI_TEMPERATURE='0.1'
```

### 生产环境
```bash
export OPENAI_BASE_URL='https://api.openai.com/v1'
export OPENAI_MODEL='gpt-4'
export OPENAI_MAX_TOKENS='3000'
export OPENAI_TEMPERATURE='0.0'
```

---

💡 **提示**: 使用环境变量是最安全和灵活的配置方式，强烈推荐！
