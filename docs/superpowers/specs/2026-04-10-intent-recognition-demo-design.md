# Intent Recognition Demo 设计文档

**设计日期：** 2026-04-10
**项目类型：** 技术验证 demo
**目标：** 验证 LangGraph Agent + MagicSkills skill_tool + intent-recognition skill 的集成可行性

---

## 1. 项目概述

### 1.1 目标

创建一个最小验证 demo，展示 LangGraph Agent 如何通过统一的 skill_tool 接口调用 MagicSkills 技能（包括 intent-recognition skill），验证三种技术栈的集成可行性。

### 1.2 核心场景

- **场景 1：意图识别** - 用户请求分析文本意图，Agent 调用 intent-recognition skill
- **场景 2：技能查询** - 用户查询可用技能，Agent 调用 MagicSkills 列出技能

### 1.3 技术栈

- **LangGraph** - ReAct Agent 架构
- **MagicSkills** - 统一的 skill 管理和调用系统
- **DeepSeek API** - LLM 服务
- **intent-recognition skill** - 银行金融场景意图识别（关键词匹配实现）

---

## 2. 架构设计

### 2.1 系统架构

```
用户输入 → LangGraph Agent (DeepSeek) → skill_tool → Skills Registry → Skills执行 → 返回结果
```

**核心特点：**
- Agent 只有**一个工具**：`skill_tool`（统一接口）
- skill_tool 支持 3 种 action：`listskill`、`readskill`、`execskill`
- 所有技能通过 skill_tool 调用，保持接口统一

### 2.2 数据流

```
┌─────────────────┐
│  预设测试场景    │
│  (Python脚本)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ LangGraph ReAct     │
│ Agent               │
│ (DeepSeek LLM)      │
└─────────┬───────────┘
          │ 分析并决定调用
          ▼
┌─────────────────────┐
│   skill_tool        │ 统一工具接口
│                     │
└─────────┬───────────┘
          │ 根据 action 路由
          ▼
┌─────────────────────┐
│ Skills Registry     │
│ - intent-recognition│
│ - pdf, xlsx, docx   │
│ - 其他 19 个技能     │
└─────────────────────┘
```

### 2.3 组件职责

| 组件 | 职责 | 技术实现 |
|------|------|---------|
| **LangGraph Agent** | 分析用户意图，决定调用哪个工具 | `create_react_agent(llm, tools)` |
| **skill_tool** | 统一的技能调用接口 | MagicSkills `skill_tool()` 函数 |
| **Skills Registry** | 管理所有已安装技能 | MagicSkills `ALL_SKILLS()` |
| **intent-recognition** | 意图识别执行脚本 | Python 关键词匹配 |

---

## 3. 文件结构设计

### 3.1 项目目录

```
/Users/liujiansmac/Desktop/njb/magicskills_langchain_agent/
│
├── intent_recognition_demo.py         # 主 demo 脚本（新增）
├── skills/                             # skills 目录（新增）
│   └── intent-recognition/             # 意图识别 skill
│       ├── SKILL.md                    # Skill规范文档（已存在）
│       ├── intent_recognition.py       # 实现脚本（新增）
│       └── requirements.txt            # 依赖清单（新增）
│
├── magicskills_api_v2.py               # HTTP API（已存在）
├── magicskills_langchain_agent.py      # Agent示例（已存在）
└── MagicSkills_LangChain_使用手册.md   # 文档（已存在）
```

### 3.2 文件职责清单

| 文件 | 职责 | 状态 | 备注 |
|------|------|------|------|
| `intent_recognition_demo.py` | 主 demo 脚本，构建 Agent，运行测试场景 | 新增 | |
| `skills/intent-recognition/SKILL.md` | Skill 规范文档（8个意图类别定义） | 新增 | 复制自 `/Users/liujiansmac/.claude/skills/intent-recognition/SKILL.md` |
| `skills/intent-recognition/intent_recognition.py` | 意图识别实现脚本（中等完整版，100-200行） | 新增 | |
| `skills/intent-recognition/requirements.txt` | Skill 依赖（可选） | 新增 | |

---

## 4. 核心实现设计

### 4.1 intent-recognition Skill 实现

**实现程度：** 中等完整版（100-200 行代码）

**核心功能：**
- 关键词匹配（8 个预定义意图类别）
- 置信度计算（简单规则：匹配关键词数量/总关键词数）
- 支持单意图和多意图场景
- 无匹配返回 `unknown`
- 基本错误处理

**意图类别定义（从 SKILL.md）：**
```python
INTENT_CATEGORIES = {
    "retail_loan_card": {
        "name": "零售贷款与信用卡",
        "keywords": ["贷款", "信用卡", "房贷", "车贷", "消费贷", "额度", "利率", "还款"]
    },
    "consumer_protection": {
        "name": "消保坐席",
        "keywords": ["投诉", "客诉", "维权", "申诉", "话术", "授权", "消保"]
    },
    "retail_analysis": {
        "name": "零售经营分析",
        "keywords": ["经营分析", "业绩", "指标", "数据分析", "报表"]
    },
    # ... 其他 5 个类别
}
```

**关键词匹配逻辑：**
```python
def recognize_intent(text: str) -> dict:
    """
    意图识别核心逻辑
    1. 遍历所有意图类别
    2. 统计每个类别匹配的关键词数量
    3. 计算置信度 = 匹配关键词数 / 该类别总关键词数
    4. 返回最高置信度的意图（>0.5）或多意图列表
    5. 置信度<0.5 返回 uncertain
    6. 无匹配返回 unknown
    """
```

**输出格式（JSON）：**
```json
{
  "intent": "consumer_protection",
  "intent_name": "消保坐席",
  "confidence": 0.85,
  "keywords": ["投诉", "信用卡"],
  "matched_category": "关键词匹配"
}
```

**多意图场景：**
```json
{
  "intents": [
    {
      "intent": "retail_loan_card",
      "confidence": 0.75,
      "keywords": ["信用卡"]
    },
    {
      "intent": "transaction_analysis",
      "confidence": 0.65,
      "keywords": ["流水"]
    }
  ],
  "primary_intent": "retail_loan_card"
}
```

### 4.2 skill_tool Wrapper 实现

**参考官方 langgraph_example/model.py 的 `_make_skill_tool` 实现：**

```python
def _make_skill_tool(skills):
    """
    将 Skills 对象包装成 LangChain tool
    参考：https://github.com/Narwhal-Lab/MagicSkills/tree/main/langgraph_example
    """
    @tool
    def skill_tool_wrapper(action: str, arg: str = "") -> str:
        """
        MagicSkills 统一工具接口。

        参数：
        - action: listskill | readskill | execskill
        - arg: skill 名称或命令参数

        示例：
        - listskill: 列出所有技能 → action="listskill", arg=""
        - readskill pdf: 读取 pdf skill文档 → action="readskill", arg="pdf"
        - execskill intent-recognition "文本": 执行意图识别 → action="execskill", arg="intent-recognition \"文本内容\""
        """
        result = skill_tool(skills, action, arg)
        return result

    return skill_tool_wrapper
```

**关键点：**
- 使用 `@tool` 装饰器包装成 LangChain 工具
- 内部调用 MagicSkills 的 `skill_tool()` 函数
- 返回字符串结果（Agent 会解析）

### 4.3 Agent 构建逻辑

**参考官方示例和现有 magicskills_langchain_agent.py：**

```python
# 1. 加载环境变量
load_dotenv(Path.home() / ".env")

# 2. 加载 Skills（包含 intent-recognition）
skills_obj = ALL_SKILLS()

# 3. 创建 tool
tools = [_make_skill_tool(skills_obj)]

# 4. 初始化 LLM（DeepSeek）
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "deepseek-chat"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.0
)

# 5. 创建 ReAct Agent
agent = create_react_agent(llm, tools)

# 6. 运行测试场景
result = agent.invoke({"messages": [("user", prompt)]})
```

### 4.4 测试场景实现

**场景 1：意图识别**
```python
prompt1 = "帮我分析一下这句话的意图：我要投诉信用卡盗刷"
result1 = agent.invoke({"messages": [("user", prompt1)]})

# 预期 Agent 执行流程：
# 1. 调用 skill_tool("listskill", "") → 了解可用技能
# 2. 调用 skill_tool("readskill", "intent-recognition") → 了解如何使用
# 3. 调用 skill_tool("execskill", "intent-recognition \"我要投诉信用卡盗刷\"") → 执行意图识别
# 4. 返回解析后的结果
```

**场景 2：技能查询**
```python
prompt2 = "有哪些可以用的技能？"
result2 = agent.invoke({"messages": [("user", prompt2)]})

# 预期 Agent 执行流程：
# 1. 调用 skill_tool("listskill", "") → 列出所有技能
# 2. 返回技能列表及描述
```

---

## 5. 运行流程设计

### 5.1 环境准备步骤

**环境说明：**
- Demo 脚本在本地 macOS 环境运行
- MagicSkills API 服务在远程 Linux 服务器（Aliyun ECS）运行
- 需要通过 SSH 或远程部署 skill 到服务器

**步骤 1：启动 MagicSkills API（远程服务器）**
```bash
# 在远程服务器执行：
nohup sudo /root/miniforge3/envs/magicskills/bin/python3 magicskills_api_v2.py \
  > /tmp/magicskills.log 2>&1 &

# 验证（本地或远程）
curl http://your-server-ip:5000/health
```

**步骤 2：安装 intent-recognition skill（远程服务器）**
```bash
# 方式一：先复制 skill 到远程服务器，再安装
# 本地执行：
scp -r /Users/liujiansmac/.claude/skills/intent-recognition \
  user@your-server:/tmp/intent-recognition

# 远程服务器执行：
sudo /root/miniforge3/envs/magicskills/bin/magicskills install \
  /tmp/intent-recognition \
  -t /home/admin/.openclaw/workspace/skills/allskills

# 方式二：通过 HTTP API 安装（如果 skill 文件已传输）
curl -X POST http://your-server-ip:5000/skills/install \
  -H "Content-Type: application/json" \
  -d '{"source":"/tmp/intent-recognition","target_root":"/home/admin/.openclaw/workspace/skills/allskills"}'

# 验证安装
curl http://your-server-ip:5000/skills | grep intent-recognition
```

**步骤 3：配置环境变量**
```bash
# 确保 ~/.env 包含：
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

### 5.2 Demo 运行步骤

```bash
# 运行 demo
sudo /root/miniforge3/envs/magicskills/bin/python3 intent_recognition_demo.py
```

**预期输出：**
```
============================================================
MagicSkills + LangGraph Agent Demo
============================================================
Skills count: 20
[初始化] 创建 LLM...
✅ LLM 创建成功
[初始化] 创建 Agent...
✅ Agent 创建成功

========================================
场景 1：意图识别
========================================
用户输入：帮我分析一下这句话的意图：我要投诉信用卡盗刷

Agent 思考过程：
[调用 skill_tool listskill]
[调用 skill_tool readskill intent-recognition]
[调用 skill_tool execskill intent-recognition "我要投诉信用卡盗刷"]

结果：
{
  "intent": "consumer_protection",
  "intent_name": "消保坐席",
  "confidence": 0.92,
  "keywords": ["投诉", "信用卡", "盗刷"]
}

Agent 最终回答：这是一个消保坐席场景...

========================================
场景 2：技能查询
========================================
用户输入：有哪些可以用的技能？

Agent 思考过程：
[调用 skill_tool listskill]

结果：找到 20 个 skills...

Agent 最终回答：当前有 20 个可用技能...
========================================
Demo 完成！
```

---

## 6. 技术细节

### 6.1 依赖项

**requirements.txt（demo）：**
```
langchain-openai>=0.1.0
langgraph>=0.0.20
python-dotenv>=1.0.0
requests>=2.31.0
```

**magicskills 安装验证：**
```bash
# 检查 magicskills 是否已安装在 Python 环境中
python -c "import magicskills; print(magicskills.__version__)"
# 或检查技能数量
python -c "from magicskills import ALL_SKILLS; print(len(ALL_SKILLS().skills))"
```

**requirements.txt（intent-recognition skill）：**
```
# 意图识别 skill 无额外依赖（纯 Python 实现）
```

### 6.2 MagicSkills skill_tool 接口说明

**官方 API：**
- `skill_tool(skills_obj, action, arg)`
- action 类型：
  - `listskill`：列出所有技能
  - `readskill <skill_name>`：读取技能文档（SKILL.md）
  - `execskill <command>`：执行技能脚本

**执行示例：**
```python
# 列出技能
skill_tool(skills, "listskill", "")
# 输出："1. pdf\n2. xlsx\n..."

# 读取文档
skill_tool(skills, "readskill", "pdf")
# 输出：pdf skill 的 SKILL.md 内容

# 执行技能
skill_tool(skills, "execskill", "intent-recognition \"我要投诉信用卡盗刷\"")
# 输出：意图识别 JSON 结果
```

### 6.3 intent-recognition.py 实现规范

**脚本接口：**
- 作为 MagicSkills skill 的执行入口
- 通过命令行参数接收文本：`python intent_recognition.py "文本内容"`
- 输出 JSON 格式字符串到 stdout

**代码结构（中等完整版）：**
```python
#!/usr/bin/env python3
"""Intent Recognition Skill - 银行金融场景意图识别"""

import sys
import json

# 意图类别定义
INTENT_CATEGORIES = {
    "retail_loan_card": {...},
    "consumer_protection": {...},
    # ... 其他 6 个
}

def recognize_intent(text: str) -> dict:
    """核心意图识别逻辑"""
    # 1. 关键词匹配
    # 2. 置信度计算
    # 3. 返回结构化结果
    pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "需要提供文本参数"}))
        sys.exit(1)

    text = sys.argv[1]
    result = recognize_intent(text)
    print(json.dumps(result, ensure_ascii=False))
```

---

## 7. 错误处理设计

### 7.1 边缘情况处理

**intent-recognition skill：**
- 无关键词匹配 → 返回 `{"intent": "unknown", "confidence": 0}`
- 多个意图置信度相近 → 返回多意图列表，标注 `primary_intent`
- 置信度 < 0.5 → 返回 `uncertain` 并提供可能选项
- 输入为空 → 返回错误提示

**Agent 层面：**
- skill_tool 调用失败 → Agent 捕获错误消息并解释
- skill 未安装 → 提示用户先安装 intent-recognition
- MagicSkills API 未启动 → 提示启动服务

### 7.2 日志记录

**demo 输出日志：**
- 每个 tool 调用的完整过程
- tool 返回的原始结果
- Agent 的最终回答

**可选：保存为 JSON 文件**
```python
# 参考 langgraph_example 的日志格式
{
  "scenario": "intent_recognition",
  "prompt": "...",
  "tool_calls": [
    {"tool": "skill_tool", "args": {...}, "result": ...}
  ],
  "final_answer": "..."
}
```

---

## 8. 成功标准

### 8.1 Demo 验证成功标准

- ✅ 场景 1：Agent 能成功调用 intent-recognition skill，返回结构化意图识别结果
- ✅ 场景 2：Agent 能成功调用 listskill，返回技能列表
- ✅ 输出清晰展示：用户输入 → Agent 思考 → 工具调用 → 结果
- ✅ intent-recognition skill 正确安装到 MagicSkills 系统
- ✅ skill_tool 接口工作正常（listskill/readskill/execskill）

### 8.2 技术验证目标

- 证明 LangGraph Agent 能通过统一的 skill_tool 调用不同技能
- 证明 intent-recognition skill 能集成到 MagicSkills 系统
- 证明 DeepSeek LLM 能正确分析和调用 skill_tool
- 证明整个流程可运行、可观测、可理解

---

## 9. 参考资源

### 9.1 官方示例

- [MagicSkills LangGraph Example](https://github.com/Narwhal-Lab/MagicSkills/tree/main/langgraph_example)
- [MagicSkills LangChain Example](https://github.com/Narwhal-Lab/MagicSkills/tree/main/langchain_example)
- [MagicSkills Python API 文档](https://github.com/Narwhal-Lab/MagicSkills/blob/main/doc/python-api.zh-CN.md)

### 9.2 项目现有资源

- `magicskills_api_v2.py` - HTTP API 实现
- `magicskills_langchain_agent.py` - LangChain Agent 示例
- `MagicSkills_API_v2_文档.md` - API 文档
- `MagicSkills_LangChain_使用手册.md` - 使用手册
- `/Users/liujiansmac/.claude/skills/intent-recognition/SKILL.md` - Skill 规范

---

## 10. 实施计划

### 10.1 实施顺序

1. **创建 intent-recognition 实现脚本**（100-200 行）
2. **创建 requirements.txt**
3. **安装 skill 到 MagicSkills 系统**
4. **创建 intent_recognition_demo.py**（主 demo 脚本）
5. **测试场景 1 和场景 2**
6. **优化输出格式和错误处理**

### 10.2 预估工作量

- intent_recognition.py 实现：1-2 小时
- intent_recognition_demo.py：1 小时
- 测试和调试：1 小时
- **总计：3-4 小时**

---

## 附录 A：intent-recognition Skill 目录结构

```
skills/intent-recognition/
├── SKILL.md                    # Skill 规范文档（已存在）
├── intent_recognition.py       # 实现脚本（新增）
└── requirements.txt            # 依赖清单（新增）

# 完整 skill 结构（可选）：
├── scripts/                    # 可选：辅助脚本
├── tests/                      # 可选：测试脚本
└── README.md                   # 可选：说明文档
```

---

## 附录 B：skill_tool 调用示例

**Python 直接调用：**
```python
from magicskills import ALL_SKILLS, skill_tool

skills = ALL_SKILLS()

# 列出技能
result = skill_tool(skills, "listskill", "")
print(result)

# 读取 skill 文档
result = skill_tool(skills, "readskill", "intent-recognition")
print(result)

# 执行 intent-recognition
result = skill_tool(skills, "execskill", "intent-recognition \"我要投诉信用卡盗刷\"")
print(result)  # JSON 格式意图识别结果
```

**HTTP API 调用：**
```bash
curl -X POST http://localhost:5000/skill-tool \
  -H "Content-Type: application/json" \
  -d '{"action":"listskill","arg":"","name":"Allskills"}'

curl -X POST http://localhost:5000/skill-tool \
  -H "Content-Type: application/json" \
  -d '{"action":"execskill","arg":"intent-recognition \"我要投诉信用卡盗刷\"","name":"Allskills"}'
```

---

**设计完成日期：** 2026-04-10
**下一步：** 进入 spec review loop，然后实施开发