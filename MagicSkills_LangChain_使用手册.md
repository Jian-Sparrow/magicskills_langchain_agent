# MagicSkills + LangChain 远程调用使用手册

> 通过 LangChain 框架远程调用 MagicSkills 技能的完整指南  
> 适用环境：DeepSeek API + MagicSkills HTTP API + LangGraph  
> 文档版本：1.0  
> 创建时间：2026-04-09

---

## 📋 目录

1. [环境准备](#1-环境准备)
2. [启动 API 服务](#2-启动-api-服务)
3. [创建 Agent 脚本](#3-创建-agent-脚本)
4. [运行测试](#4-运行测试)
5. [使用示例](#5-使用示例)
6. [API 端点参考](#6-api-端点参考)
7. [常见问题](#7-常见问题)
8. [附录：完整代码](#8-附录完整代码)

---

## 1. 环境准备

### 1.1 确认 MagicSkills 环境

```bash
# 检查 magicskills 环境是否存在
ls -la /root/miniforge3/envs/magicskills/

# 验证 magicskills 已安装
sudo /root/miniforge3/envs/magicskills/bin/python3 -c "import magicskills; print('OK')"
```

**预期输出：** `OK`

### 1.2 配置 DeepSeek API Key

编辑 `~/.env` 文件：

```bash
cat ~/.env
```

**确保包含以下内容：**

```ini
OPENAI_API_KEY=sk-你的 deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

> 💡 **说明：**
> - `OPENAI_API_KEY`：你的 DeepSeek API 密钥
> - `OPENAI_BASE_URL`：DeepSeek API 地址
> - `OPENAI_MODEL`：使用的模型名称（deepseek-chat 或 deepseek-coder）

### 1.3 安装依赖

```bash
# 检查依赖是否已安装
sudo /root/miniforge3/envs/magicskills/bin/python3 -c "from langchain_openai import ChatOpenAI; from langgraph.prebuilt import create_react_agent; print('OK')"
```

如果报错，安装依赖：

```bash
sudo /root/miniforge3/envs/magicskills/bin/pip3 install langchain langchain-openai langgraph requests python-dotenv flask
```

---

## 2. 启动 API 服务

### 2.1 后台启动 MagicSkills API

```bash
nohup sudo /root/miniforge3/envs/magicskills/bin/python3 /home/admin/.openclaw/workspace/magicskills_api_v2.py > /tmp/magicskills.log 2>&1 &
```

### 2.2 验证服务启动成功

```bash
curl http://localhost:5000/health
```

**预期输出：**

```json
{
  "status": "ok",
  "service": "magicskills-api",
  "skills_count": 19,
  "collections_count": 2
}
```

### 2.3 管理命令

```bash
# 查看 API 日志
tail -f /tmp/magicskills.log

# 检查端口占用
netstat -tlnp | grep 5000

# 停止 API 服务
pkill -f "python magicskills_api_v2"

# 重启服务
pkill -f "python magicskills_api_v2"
nohup sudo /root/miniforge3/envs/magicskills/bin/python3 /home/admin/.openclaw/workspace/magicskills_api_v2.py > /tmp/magicskills.log 2>&1 &
```

---

## 3. 创建 Agent 脚本

### 3.1 脚本位置

`/home/admin/.openclaw/workspace/magicskills_langchain_agent.py`

### 3.2 脚本结构说明

脚本包含以下核心部分：

1. **环境变量加载**：从 `~/.env` 读取 DeepSeek 配置
2. **工具定义**：使用 `@tool` 装饰器定义 5 个 MagicSkills 工具
3. **LLM 初始化**：创建 DeepSeek ChatOpenAI 实例
4. **Agent 创建**：使用 LangGraph 的 `create_react_agent` 创建 ReAct Agent
5. **运行入口**：从命令行获取查询并执行

### 3.3 工具列表

| 工具名称 | 功能 | 输入参数 |
|---------|------|---------|
| `list_skills` | 列出所有可用技能 | 无 |
| `read_skill` | 读取技能文档 | skill_name (技能名称) |
| `search_skills` | 搜索技能 | query (搜索关键词) |
| `list_collections` | 列出技能集合 | 无 |
| `call_skill_tool` | 调用统一接口 | action, arg |

---

## 4. 运行测试

### 4.1 基本用法

```bash
sudo /root/miniforge3/envs/magicskills/bin/python3 /home/admin/.openclaw/workspace/magicskills_langchain_agent.py "你的问题"
```

### 4.2 第一次运行测试

```bash
sudo /root/miniforge3/envs/magicskills/bin/python3 magicskills_langchain_agent.py "有哪些处理 PDF 的技能？"
```

**预期输出：**

```
============================================================
MagicSkills + LangChain Agent (DeepSeek)
============================================================
API Base: http://localhost:5000
LLM Model: deepseek-chat
LLM Base URL: https://api.deepseek.com/v1

[初始化] 创建 LLM...
✅ LLM 创建成功
[初始化] 创建 Agent...
✅ Agent 创建成功

查询：有哪些处理 PDF 的技能？
============================================================

============================================================
回答：根据搜索结果，目前有以下处理 PDF 的技能：

## 1. **PDF 技能 (主要技能)**
这是专门处理 PDF 文件的核心技能，支持以下功能：
...
```

---

## 5. 使用示例

### 5.1 查询类任务

```bash
# 列出所有技能
sudo /root/miniforge3/envs/magicskills/bin/python3 magicskills_langchain_agent.py "有哪些可用的技能？"

# 搜索特定功能
sudo /root/miniforge3/envs/magicskills/bin/python3 magicskills_langchain_agent.py "帮我找处理 Excel 的技能"

# 查询集合
sudo /root/miniforge3/envs/magicskills/bin/python3 magicskills_langchain_agent.py "有哪些技能集合？"
```

### 5.2 读取文档

```bash
# 读取具体技能文档
sudo /root/miniforge3/envs/magicskills/bin/python3 magicskills_langchain_agent.py "读取 pdf 技能的详细文档"

# 读取多个技能
sudo /root/miniforge3/envs/magicskills/bin/python3 magicskills_langchain_agent.py "帮我看看 docx 和 xlsx 技能分别是什么"
```

### 5.3 执行操作

```bash
# 执行技能命令
sudo /root/miniforge3/envs/magicskills/bin/python3 magicskills_langchain_agent.py "列出 allskills 集合里的所有技能"
```

---

## 6. API 端点参考

### 6.1 基础信息

| 端点 | 方法 | 说明 | 示例 |
|------|------|------|------|
| `/` | GET | API 首页 | `curl http://localhost:5000/` |
| `/health` | GET | 健康检查 | `curl http://localhost:5000/health` |

### 6.2 技能查询

| 端点 | 方法 | 说明 | 示例 |
|------|------|------|------|
| `/skills` | GET | 列出所有技能 | `curl http://localhost:5000/skills` |
| `/skills/<name>` | GET | 获取技能详情 | `curl http://localhost:5000/skills/pdf` |
| `/skills/<name>/content` | GET | 读取技能文档 | `curl http://localhost:5000/skills/pdf/content` |
| `/skills/search` | POST | 搜索技能 | `curl -X POST http://localhost:5000/skills/search -H "Content-Type: application/json" -d '{"query":"pdf"}'` |

### 6.3 集合管理

| 端点 | 方法 | 说明 | 示例 |
|------|------|------|------|
| `/collections` | GET | 列出所有集合 | `curl http://localhost:5000/collections` |
| `/collections/<name>` | GET | 获取集合详情 | `curl http://localhost:5000/collections/Allskills` |

### 6.4 技能工具

| 端点 | 方法 | 说明 | 示例 |
|------|------|------|------|
| `/skill-tool` | POST | 统一工具接口 | `curl -X POST http://localhost:5000/skill-tool -H "Content-Type: application/json" -d '{"action":"listskill","arg":"","name":"Allskills"}'` |
| `/skills/execute` | POST | 执行技能命令 | `curl -X POST http://localhost:5000/skills/execute -H "Content-Type: application/json" -d '{"command":"ls -la"}'` |

---

## 7. 常见问题

### Q1: API 服务启动失败

**症状：** `curl http://localhost:5000/health` 返回连接错误

**解决方案：**

```bash
# 1. 检查端口是否被占用
netstat -tlnp | grep 5000

# 2. 查看错误日志
tail -f /tmp/magicskills.log

# 3. 重新启动服务
pkill -f "python magicskills_api_v2"
nohup sudo /root/miniforge3/envs/magicskills/bin/python3 /home/admin/.openclaw/workspace/magicskills_api_v2.py > /tmp/magicskills.log 2>&1 &
```

### Q2: DeepSeek API 调用失败

**症状：** `Invalid API key` 或 `401 Unauthorized`

**解决方案：**

```bash
# 1. 检查 .env 文件配置
cat ~/.env

# 2. 测试 API key 是否有效
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer sk-你的 key"

# 3. 确保环境变量正确加载
sudo /root/miniforge3/envs/magicskills/bin/python3 -c "from dotenv import load_dotenv; from pathlib import Path; load_dotenv(Path.home() / '.env'); import os; print(os.getenv('OPENAI_API_KEY')[:10])"
```

### Q3: LangChain 版本不兼容

**症状：** `ImportError: cannot import name 'create_react_agent'`

**解决方案：**

```bash
# 升级 langgraph
sudo /root/miniforge3/envs/magicskills/bin/pip3 install --upgrade langgraph langchain langchain-openai
```

### Q4: Agent 响应慢或超时

**症状：** 查询后长时间无响应

**解决方案：**

1. 检查 DeepSeek API 连接是否正常
2. 增加脚本中的 `timeout` 参数值
3. 使用更简单的查询

### Q5: 找不到 magicskills 模块

**症状：** `ModuleNotFoundError: No module named 'magicskills'`

**解决方案：**

```bash
# 确认使用正确的 Python 环境
sudo /root/miniforge3/envs/magicskills/bin/python3 -c "import magicskills; print('OK')"

# 如果失败，重新安装 magicskills
cd /home/admin/.openclaw/workspace/MagicSkills
sudo /root/miniforge3/envs/magicskills/bin/pip3 install -e .
```

---

## 8. 附录：完整代码

### 8.1 Agent 脚本完整代码

文件：`/home/admin/.openclaw/workspace/magicskills_langchain_agent.py`

```python
#!/usr/bin/env python3
"""
MagicSkills + LangChain 集成脚本（DeepSeek 配置）- 使用 LangGraph

用法:
    sudo /root/miniforge3/envs/magicskills/bin/python3 magicskills_langchain_agent.py "你的问题"
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import requests

# 加载 .env 文件（root 目录）
load_dotenv(Path.home() / ".env")

# API 配置
API_BASE = "http://localhost:5000"

# LLM 配置（从环境变量读取）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")

print("=" * 60)
print("MagicSkills + LangChain Agent (DeepSeek)")
print("=" * 60)
print(f"API Base: {API_BASE}")
print(f"LLM Model: {OPENAI_MODEL}")
print(f"LLM Base URL: {OPENAI_BASE_URL}")
print()

# ============ 定义工具 ============

@tool
def list_skills():
    """列出所有可用的 MagicSkills。当你需要了解有哪些技能可用时调用。"""
    try:
        resp = requests.get(f"{API_BASE}/skills", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        skills_list = [s['name'] for s in data['skills']]
        return f"找到 {data['count']} 个 skills: {', '.join(skills_list)}"
    except Exception as e:
        return f"API 调用失败：{str(e)}"


@tool
def read_skill(skill_name: str):
    """读取指定技能的文档内容。输入技能名称，如 'pdf', 'docx', 'xlsx'。"""
    try:
        resp = requests.get(f"{API_BASE}/skills/{skill_name}/content", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data['content']
    except Exception as e:
        return f"API 调用失败：{str(e)}"


@tool
def search_skills(query: str):
    """根据关键词搜索技能。输入搜索词，如 'PDF', 'Excel', '代码转换'。"""
    try:
        resp = requests.post(f"{API_BASE}/skills/search", json={"query": query}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        skills_list = [s['name'] for s in data['skills']]
        return f"找到 {data['count']} 个匹配 '{query}' 的技能：{', '.join(skills_list)}"
    except Exception as e:
        return f"API 调用失败：{str(e)}"


@tool
def list_collections():
    """列出所有技能集合。当你需要了解有哪些技能集合时调用。"""
    try:
        resp = requests.get(f"{API_BASE}/collections", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        collections = [c['name'] for c in data['collections']]
        return f"找到 {len(collections)} 个集合：{', '.join(collections)}"
    except Exception as e:
        return f"API 调用失败：{str(e)}"


@tool
def call_skill_tool(action: str, arg: str = ""):
    """调用 MagicSkills 统一接口。action 可选：listskill, readskill, execskill。arg 是操作参数。"""
    try:
        resp = requests.post(
            f"{API_BASE}/skill-tool",
            json={"action": action, "arg": arg, "name": "Allskills"},
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get('result', str(data))
    except Exception as e:
        return f"API 调用失败：{str(e)}"


# ============ 创建工具列表 ============

tools = [list_skills, read_skill, search_skills, list_collections, call_skill_tool]

# ============ 初始化 LLM ============

print("[初始化] 创建 LLM...")
llm = ChatOpenAI(
    model=OPENAI_MODEL,
    base_url=OPENAI_BASE_URL,
    api_key=OPENAI_API_KEY,
    temperature=0.0,
)
print("✅ LLM 创建成功")

# ============ 创建 Agent ============

print("[初始化] 创建 Agent...")
agent = create_react_agent(llm, tools)
print("✅ Agent 创建成功")

# ============ 运行 ============

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "有哪些处理 PDF 的技能？"
    
    print(f"\n查询：{query}")
    print("=" * 60)
    
    result = agent.invoke({"messages": [("user", query)]})
    
    # 获取最后一条消息（助手的回答）
    output = result["messages"][-1].content
    
    print("\n" + "=" * 60)
    print(f"回答：{output}")
```

### 8.2 快速启动脚本

创建 `/home/admin/.openclaw/workspace/run_magicskills_agent.sh`：

```bash
#!/bin/bash
# MagicSkills Agent 快速启动脚本

QUERY="$1"

if [ -z "$QUERY" ]; then
    echo "用法：$0 '你的问题'"
    echo "示例：$0 '有哪些处理 PDF 的技能？'"
    exit 1
fi

# 检查 API 服务
if ! curl -s http://localhost:5000/health > /dev/null; then
    echo "⚠️  API 服务未运行，正在启动..."
    nohup sudo /root/miniforge3/envs/magicskills/bin/python3 /home/admin/.openclaw/workspace/magicskills_api_v2.py > /tmp/magicskills.log 2>&1 &
    sleep 3
fi

# 运行 Agent
cd /home/admin/.openclaw/workspace
sudo /root/miniforge3/envs/magicskills/bin/python3 magicskills_langchain_agent.py "$QUERY"
```

赋予执行权限：

```bash
chmod +x /home/admin/.openclaw/workspace/run_magicskills_agent.sh
```

使用：

```bash
./run_magicskills_agent.sh "有哪些处理 PDF 的技能？"
```

---

## 📚 参考资源

- [MagicSkills 官方文档](https://github.com/Narwhal-Lab/MagicSkills)
- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)

---

**文档版本**: 1.0  
**创建时间**: 2026-04-09  
**适用环境**: Linux (Aliyun ECS)  
**维护者**: 空崎日奈
