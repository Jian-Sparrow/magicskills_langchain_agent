# MagicSkills + LangChain 意图识别系统技术文档

## 目录

1. [MagicSkills 系统概述](#1-magicskills-系统概述)
2. [技能注册与发现机制](#2-技能注册与发现机制)
3. [Intent-recognition 技能实现](#3-intent-recognition-技能实现)
4. [LangChain/LangGraph 集成方案](#4-langchainlanggraph-集成方案)
5. [总结与展望](#5-总结与展望)

---

## 1. MagicSkills 系统概述

### 1.1 什么是 MagicSkills

MagicSkills 是一个基于 Python 的技能管理框架，提供统一的技能注册、发现和执行机制。它通过标准化的 `SKILL.md` 文档定义技能元信息，支持技能的动态注册、查询和调用。

**核心特性：**

- **技能标准化**：每个技能通过 `SKILL.md` 定义名称、描述、使用方法
- **自动发现机制**：扫描技能目录，解析 frontmatter 自动注册技能
- **统一调用接口**：提供 `skill_tool` 统一工具函数，支持 `listskill`、`readskill`、`execskill` 操作
- **集合管理**：支持多个技能集合（Skills），每个集合可包含多个技能
- **HTTP API 扩展**：可将技能功能通过 Flask API 暴露为 HTTP 服务

### 1.2 核心架构

```
┌─────────────────────────────────────────────────┐
│           MagicSkills Framework                  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Skills Registry (全局注册表)              │  │
│  │  - 管理多个 Skills 集合                    │  │
│  │  - 提供查询和访问接口                      │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                            │
│  ┌──────────────────────────────────────────┐  │
│  │  Skills Collection (技能集合)              │  │
│  │  - Allskills (全局技能集合)                │  │
│  │  - Custom Collections (自定义集合)         │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                            │
│  ┌──────────────────────────────────────────┐  │
│  │  Skill Instance (单个技能)                 │  │
│  │  - SKILL.md (元信息定义)                   │  │
│  │  - Python Script (执行逻辑)                │  │
│  │  - requirements.txt (依赖)                 │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Python API Functions                      │  │
│  │  - listskill(skills)  列出技能             │  │
│  │  - readskill(skills, name) 读取文档        │  │
│  │  - showskill(skills, name) 显示详情        │  │
│  │  - execskill(skills, cmd) 执行技能         │  │
│  │  - addskill(skills, target) 添加技能       │  │
│  │  - skill_tool(skills, action, arg) 统一接口│  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  HTTP API Server (Flask)                   │  │
│  │  - GET /skills  列出所有技能                │  │
│  │  - GET /skills/<name>  获取技能详情         │  │
│  │  - GET /skills/<name>/content  读取文档     │  │
│  │  - POST /skill-tool  统一调用接口           │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 1.3 核心组件详解

#### Skills Registry（全局注册表）

```python
from magicskills import REGISTRY

# Registry 是全局单例，管理所有 Skills 集合
REGISTRY.register(skills_obj)  # 注册技能集合
REGISTRY.get_skills(name)      # 获取指定集合
REGISTRY.list_all()            # 列出所有集合
```

#### Skills Collection（技能集合）

```python
from magicskills import Skills

# 创建技能集合，扫描指定目录
all_skills = Skills(
    name="Allskills",
    paths=["/app/workspace/skills/allskills"],  # 技能目录路径
    agent_md_path="/app/workspace/AGENTS.md"    # Agent 配置文件
)

# Skills 对象属性
all_skills.name             # 集合名称
all_skills.skills           # 技能列表（List[Skill]）
all_skills.tool_description # 工具描述（用于 LangChain）
all_skills.cli_description  # CLI 描述
```

#### Skill Instance（单个技能）

每个技能必须包含以下文件：

```
intent-recognition/
├── SKILL.md           # 技能元信息定义（必需）
├── intent_recognition.py  # 执行脚本（必需）
└── requirements.txt   # Python 依赖（可选）
```

**SKILL.md 文件格式：**

```markdown
---
name: intent-recognition
description: 从用户文本中提取意图信息并进行分类
---

# Intent Recognition Skill

## Quick Start
...
```

frontmatter 部分（`---` 包裹的 YAML）定义技能元信息：
- `name`: 技能唯一标识
- `description`: 技能描述

### 1.4 关键 Python API

| 函数 | 功能 | 示例 |
|------|------|------|
| `listskill(skills)` | 列出所有技能 | `listskill(ALL_SKILLS())` |
| `readskill(skills, name)` | 读取技能文档 | `readskill(ALL_SKILLS(), "intent-recognition")` |
| `showskill(skills, name)` | 显示技能详情 | `showskill(ALL_SKILLS(), "intent-recognition")` |
| `execskill(skills, cmd)` | 执行技能命令 | `execskill(ALL_SKILLS(), "intent-recognition '文本'")` |
| `addskill(skills, target)` | 添加技能 | `addskill(ALL_SKILLS(), "./my-skill")` |
| `skill_tool(skills, action, arg)` | 统一工具接口 | `skill_tool(ALL_SKILLS(), "listskill", "")` |

**统一接口 `skill_tool`：**

```python
# 列出所有技能
skill_tool(ALL_SKILLS(), "listskill", "")
# 输出：技能列表文本

# 读取技能文档
skill_tool(ALL_SKILLS(), "readskill", "intent-recognition")
# 输出：SKILL.md 内容

# 执行技能
skill_tool(ALL_SKILLS(), "execskill", "intent-recognition '我要投诉'")
# 输出：技能执行结果（JSON）
```

---

## 2. 技能注册与发现机制

### 2.1 技能发现流程

MagicSkills 通过扫描技能目录并解析 `SKILL.md` frontmatter 自动发现技能。

**发现流程：**

```
Skills(paths=[skills_dir])
    ↓
扫描 skills_dir 目录
    ↓
查找所有子目录中的 SKILL.md 文件
    ↓
解析 SKILL.md frontmatter (YAML)
    ↓
提取 name、description 等元信息
    ↓
创建 Skill 对象
    ↓
添加到 skills.skills 列表
    ↓
注册到 REGISTRY
```

**源码解析（简化版）：**

```python
class Skills:
    def __init__(self, name, paths, agent_md_path):
        self.name = name
        self.skills = []

        # 扫描所有路径
        for path in paths:
            self._discover_skills(path)

        # 注册到全局 Registry
        REGISTRY.register(self)

    def _discover_skills(self, base_dir):
        """扫描目录，发现所有 SKILL.md"""
        base_path = Path(base_dir)

        # 遍历子目录
        for skill_dir in base_path.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    # 解析 frontmatter
                    skill = self._parse_skill_md(skill_md, skill_dir)
                    self.skills.append(skill)

    def _parse_skill_md(self, skill_md_path, skill_dir):
        """解析 SKILL.md 文件"""
        content = skill_md_path.read_text()

        # 提取 YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---")
            yaml_content = parts[1].strip()
            metadata = yaml.safe_load(yaml_content)

            # 创建 Skill 对象
            return Skill(
                name=metadata.get("name"),
                description=metadata.get("description"),
                path=skill_md_path,
                base_dir=skill_dir,
                # ... 其他属性
            )
```

### 2.2 技能注册关键步骤

**步骤 1：创建 Skills 集合**

```python
from magicskills import Skills, REGISTRY

# 使用环境变量配置路径（支持多环境部署）
import os
SKILLS_DIR = os.getenv("SKILLS_DIR", "/app/workspace/skills/allskills")
AGENTS_MD_PATH = os.getenv("AGENTS_MD_PATH", "/app/workspace/AGENTS.md")

# 创建 Allskills 集合
all_skills = Skills(
    name="Allskills",
    paths=[SKILLS_DIR],
    agent_md_path=AGENTS_MD_PATH
)
```

**步骤 2：自动发现技能**

Skills 对象创建时自动扫描 `SKILLS_DIR` 目录，发现 intent-recognition 技能：

```
SKILLS_DIR=/app/workspace/skills/allskills
    ↓
扫描子目录：
    intent-recognition/
        ├── SKILL.md ✅  存在
        ├── intent_recognition.py
        └── requirements.txt
    ↓
解析 SKILL.md frontmatter:
    name: intent-recognition
    description: 从用户文本中提取意图信息...
    ↓
创建 Skill 对象：
    Skill(name="intent-recognition", ...)
    ↓
添加到 all_skills.skills 列表
```

**步骤 3：注册到全局 Registry**

```python
# 注册到全局 Registry
REGISTRY.register(all_skills)

# 现在可以通过 Registry 访问
REGISTRY.get_skills("Allskills")
# 返回: all_skills 对象（包含 intent-recognition 技能）
```

**步骤 4：覆盖 ALL_SKILLS() 函数（关键步骤）**

在 `magicskills_api_v2_docker.py` 中，我们主动初始化并覆盖 `ALL_SKILLS()` 函数：

```python
# 初始化 Allskills 集合（使用环境变量配置的路径）
def init_all_skills():
    """初始化 Allskills 集合并注册到全局 REGISTRY"""
    try:
        # 创建 Skills 对象，扫描 SKILLS_DIR 目录
        all_skills = Skills(
            name="Allskills",
            paths=[str(SKILLS_DIR)],
            agent_md_path=str(AGENTS_MD_PATH)
        )
        # 注册到全局 REGISTRY
        REGISTRY.register(all_skills)
        print(f"✅ Initialized Allskills with {len(all_skills.skills)} skills")
        return all_skills
    except Exception as e:
        print(f"❌ Failed to initialize Allskills: {e}")
        return None

# 模块加载时立即初始化（关键！）
_ALL_SKILLS_INSTANCE = init_all_skills()

# 覆盖 ALL_SKILLS 函数以使用我们的实例
def ALL_SKILLS():
    """返回初始化的 Allskills 实例"""
    return _ALL_SKILLS_INSTANCE or Skills(name="Allskills", paths=[str(SKILLS_DIR)])
```

**为什么需要主动初始化？**

在原始版本（`magicskills_api_v2.py`）中，`ALL_SKILLS()` 函数依赖于外部环境，可能无法正确初始化，导致 `skills_count=0`。

通过主动初始化 `_ALL_SKILLS_INSTANCE`，确保模块加载时就完成技能发现和注册，解决技能无法被发现的问题。

### 2.3 技能发现失败排查

**常见问题：**

1. **SKILL.md 文件不存在**
   - 技能目录必须包含 `SKILL.md` 文件
   - 文件名必须是 `SKILL.md`（大小写敏感）

2. **frontmatter 格式错误**
   - YAML 部分必须用 `---` 包裹
   - 必须包含 `name` 和 `description` 字段

3. **路径配置错误**
   - 环境中路径必须正确配置（可通过环境变量）
   - 确保路径存在且可访问

**调试方法：**

```python
# 检查技能数量
from magicskills import ALL_SKILLS
skills = ALL_SKILLS()
print(f"Skills count: {len(skills.skills)}")

# 检查技能目录
import os
skills_dir = os.getenv("SKILLS_DIR")
print(f"Skills directory: {skills_dir}")

# 检查 SKILL.md 是否存在
from pathlib import Path
skill_md = Path(skills_dir) / "intent-recognition" / "SKILL.md"
print(f"SKILL.md exists: {skill_md.exists()}")
```

---

## 3. Intent-recognition 技能实现

### 3.1 技能概述

Intent-recognition 是一个银行金融场景的意图识别技能，使用 LLM（大语言模型）进行语义理解，而非传统的关键词匹配规则。

**核心特性：**

- **LLM 驱动**：使用 LangChain + DashScope（阿里云通义千问）进行语义分析
- **语义优先**：识别关键词的语义重要性，而非简单计数
- **多意图识别**：支持识别文本中的多个意图并推荐主意图
- **可解释性**：提供 `reasoning` 字段说明识别理由

### 3.2 技能文件结构

```
intent-recognition/
├── SKILL.md               # 技能元信息定义
├── intent_recognition.py  # 核心实现脚本
└── requirements.txt       # Python 依赖
```

**requirements.txt:**

```
langchain>=0.1.0
langchain-openai>=0.1.0
langchain-core>=0.1.7
python-dotenv==1.0.0
```

### 3.3 意图类别体系

预定义 8 个银行金融场景意图类别：

| Intent ID | Intent Name | Description | Keywords |
|-----------|-------------|-------------|----------|
| `retail_loan_card` | 零售贷款与信用卡 | 零售贷款与信用卡业务 | 贷款、信用卡、房贷、车贷、额度、利率、还款... |
| `consumer_protection` | 消保坐席 | 投诉专席客服处理客诉 | 投诉、客诉、维权、申诉、投诉专席、话术... |
| `retail_analysis` | 零售经营分析 | 零售业务经营分析 | 经营分析、业绩、指标、数据分析、报表... |
| `wealth_party_building` | 南银理财党建 | 理财产品党建 | 南银理财、党建、理财产品、党建活动... |
| `credit_knowledge` | 信贷知识 | 信贷知识查询 | 信贷、信贷政策、信贷流程、信贷知识... |
| `transaction_analysis` | 流水分析 | 账户流水分析 | 流水、账户流水、流水分析、流水查询... |
| `quarterly_summary` | 综合部季度材料总结 | 综合部门季度材料汇总 | 综合部、季度材料、季度总结、材料总结... |
| `yunshuantong` | 云算通财资产品 | 云算通财资产品 | 云算通、财资产品、云算通产品、财资... |

**意图类别定义（代码）：**

```python
INTENT_CATEGORIES = {
    "retail_loan_card": {
        "name": "零售贷款与信用卡",
        "description": "零售条线，零售贷款与信用卡业务相关内容",
        "keywords": ["贷款", "信用卡", "房贷", "车贷", ...]
    },
    "consumer_protection": {
        "name": "消保坐席",
        "description": "投诉专席客服处理客诉，智能助手赋能话术查询和授权",
        "keywords": ["投诉", "客诉", "维权", "申诉", ...]
    },
    # ... 其他 6 个类别
}
```

### 3.4 LLM 驱动的意图识别流程

```
用户输入文本
    ↓
构建意图识别 Prompt
    ↓
注入意图类别体系（8 个类别 + 关键词）
    ↓
注入输出格式要求（JSON）
    ↓
注入识别原则（语义优先、权重判断）
    ↓
调用 LLM（DashScope qwen3-max）
    ↓
LLM 语义分析
    ↓
提取关键词 + 判断权重
    ↓
匹配意图类别 + 计算置信度
    ↓
生成 JSON 输出
    ↓
解析 JSON 并返回结果
```

**核心实现代码：**

#### Step 1: 构建 Prompt

```python
def create_intent_prompt(text: str) -> str:
    """构建意图识别的 Prompt"""

    # 构建意图类别描述
    intent_desc = "\n".join([
        f"- {intent_id}: {info['name']} - {info['description']}\n  关键词提示: {', '.join(info['keywords'][:5])}"
        for intent_id, info in INTENT_CATEGORIES.items()
    ])

    prompt = f"""你是一个专业的银行金融场景意图识别专家。请分析以下用户文本，识别其意图并返回结构化的 JSON 结果。

# 预定义意图类别体系

{intent_desc}

# 输出格式要求

请严格按照以下 JSON 格式输出：

单意图输出格式示例：
{{
  "intent": "retail_loan_card",
  "intent_name": "零售贷款与信用卡",
  "confidence": 0.85,
  "keywords": ["信用卡", "额度"],
  "matched_category": "关键词匹配",
  "reasoning": "识别理由说明"
}}

多意图输出格式示例：
{{
  "intents": [
    {{
      "intent": "retail_loan_card",
      "intent_name": "零售贷款与信用卡",
      "confidence": 0.82,
      "keywords": ["信用卡"]
    }},
    {{
      "intent": "credit_knowledge",
      "intent_name": "信贷知识",
      "confidence": 0.75,
      "keywords": ["信贷政策"]
    }}
  ],
  "primary_intent": "retail_loan_card",
  "reasoning": "选择主要意图的理由"
}}

# 识别原则

1. 语义优先：优先考虑文本的语义含义，而不是关键词数量
2. 权重判断：某些关键词语义重要性更高（如"投诉"比"信用卡"更明确表示意图）
3. 置信度计算：高置信度 0.8-1.0 表示语义明确关键词清晰
4. 多意图判断：文本包含多个明确且独立的意图时返回多意图结果
5. 主意图选择：多意图场景中，选择语义最明确或用户最关注的意图作为 primary_intent

# 用户输入文本

{text}

# 请输出意图识别结果（仅输出 JSON 格式，不要其他文字）"""

    return prompt
```

#### Step 2: 调用 LLM

```python
def recognize_intent_with_llm(text: str) -> dict:
    """使用 LLM 进行意图识别"""

    # 初始化 LLM（DashScope qwen3-max）
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "qwen3-max"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.0  # 低温度保证输出稳定性
    )

    # 构建 prompt
    prompt = create_intent_prompt(text)

    # 调用 LLM
    response = llm.invoke([HumanMessage(content=prompt)])

    # 提取 JSON 结果
    response_text = response.content.strip()

    # 尝试解析 JSON
    # （处理 LLM 可能输出 markdown 代码块的情况）
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()

    result = json.loads(response_text)

    # 验证必要字段
    if "intent" in result or "intents" in result:
        return result
    else:
        return {
            "intent": "unknown",
            "confidence": 0,
            "keywords": [],
            "reason": f"LLM 返回格式错误"
        }
```

#### Step 3: 输出示例

**单意图识别示例：**

```json
{
  "intent": "transaction_analysis",
  "intent_name": "流水分析",
  "confidence": 0.92,
  "keywords": ["账户流水", "流水"],
  "matched_category": "关键词匹配",
  "reasoning": "用户明确提到'查询上个月的账户流水明细'，其中'账户流水'和'流水'均为流水分析类别的核心关键词，语义清晰且意图明确。"
}
```

**多意图识别示例（语义优先）：**

输入：`"我要投诉信用卡盗刷"`

```json
{
  "intents": [
    {
      "intent": "consumer_protection",
      "intent_name": "消保坐席",
      "confidence": 0.92,
      "keywords": ["投诉"]
    },
    {
      "intent": "retail_loan_card",
      "intent_name": "零售贷款与信用卡",
      "confidence": 0.85,
      "keywords": ["信用卡"]
    }
  ],
  "primary_intent": "consumer_protection",
  "reasoning": "用户明确表达'投诉'意图，且涉及信用卡盗刷属于典型的客诉场景，消保坐席为首要处理渠道，因此将 consumer_protection 作为主意图。"
}
```

**关键改进：LLM 语义优先 vs 关键词计数**

传统关键词规则匹配的问题：
- 仅统计关键词数量，忽略语义重要性
- `"我要投诉信用卡盗刷"` → 关键词规则返回 `retail_loan_card`（匹配"信用卡"、"用卡"）
- 但语义上应该返回 `consumer_protection`（"投诉"意图更明确）

LLM 语义理解的改进：
- 识别关键词的语义权重（"投诉" > "信用卡"）
- 理解业务场景（信用卡盗刷投诉是典型客诉场景）
- 返回正确的主意图：`consumer_protection`
- 提供 `reasoning` 说明识别理由，增强可解释性

### 3.5 技能执行入口

```python
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "需要提供文本参数",
            "usage": "python intent_recognition.py \"文本内容\""
        }, ensure_ascii=False))
        sys.exit(1)

    text = sys.argv[1]
    result = recognize_intent_with_llm(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

**命令行调用：**

```bash
python intent_recognition.py "我要投诉信用卡盗刷"
# 输出：JSON 格式的意图识别结果
```

---

## 4. LangChain/LangGraph 集成方案

### 4.1 集成架构

MagicSkills 通过 HTTP API 与 LangChain/LangGraph Agent 集成。

```
┌──────────────────────────────────────────────────┐
│  LangGraph ReAct Agent                            │
│                                                   │
│  ┌────────────────────────────────────────────┐ │
│  │  LLM (ChatOpenAI - DashScope qwen3-max)     │ │
│  └────────────────────────────────────────────┘ │
│                        ↓                          │
│  ┌────────────────────────────────────────────┐ │
│  │  Tools (技能工具)                            │ │
│  │                                              │ │
│  │  @tool                                       │ │
│  │  def skill_tool_wrapper(action, arg):       │ │
│  │      """通过 HTTP API 调用 MagicSkills"""   │ │
│  │      resp = requests.post(                  │ │
│  │          "http://localhost:5002/skill-tool",│ │
│  │          json={"action": action, "arg": arg}│ │
│  │      )                                      │ │
│  │      return resp.json()["result"]           │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
                        ↓ HTTP API
┌──────────────────────────────────────────────────┐
│  MagicSkills HTTP API Server (Flask)             │
│                                                   │
│  POST /skill-tool                                │
│  {                                                │
│    "action": "listskill | readskill | execskill",│
│    "arg": "skill 名称或命令",                     │
│    "name": "Allskills"                            │
│  }                                                │
│                                                   │
│  ↓ skill_tool(ALL_SKILLS(), action, arg)         │
│                                                   │
│  返回：技能执行结果（字符串或 JSON）              │
└──────────────────────────────────────────────────┘
                        ↓ Python API
┌──────────────────────────────────────────────────┐
│  MagicSkills Python API                           │
│                                                   │
│  skill_tool(skills, action, arg)                 │
│  ↓                                               │
│  执行技能（如 intent-recognition）                │
│  ↓                                               │
│  返回技能结果                                     │
└──────────────────────────────────────────────────┘
```

### 4.2 HTTP API 包装的 skill_tool

**intent_recognition_demo.py 核心实现：**

```python
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import requests

# MagicSkills API 地址
API_BASE = "http://localhost:5002"

def _make_skill_tool(api_base: str):
    """通过 HTTP API 包装 MagicSkills skill_tool"""

    @tool
    def skill_tool_wrapper(action: str, arg: str = "") -> str:
        """
        MagicSkills 统一工具接口（HTTP API 版）。

        参数：
        - action: listskill | readskill | execskill
        - arg: skill 名称或命令参数

        示例：
        - action="listskill", arg="" → 列出所有技能
        - action="readskill", arg="pdf" → 读取 pdf skill 文档
        - action="execskill", arg="intent-recognition \"文本内容\"" → 执行意图识别
        """
        try:
            resp = requests.post(
                f"{api_base}/skill-tool",
                json={
                    "action": action,
                    "arg": arg,
                    "name": "Allskills"
                },
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get('result', str(data))
        except Exception as e:
            return f"API 调用失败：{str(e)}"

    return skill_tool_wrapper

# 创建 tool
tools = [_make_skill_tool(API_BASE)]
```

### 4.3 创建 ReAct Agent

```python
from langchain_openai import ChatOpenAI

# 初始化 LLM
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL"),      # qwen3-max
    base_url=os.getenv("OPENAI_BASE_URL"), # DashScope
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.0
)

# 创建 ReAct Agent
agent = create_react_agent(llm, tools)
```

**ReAct Agent 工作流程：**

```
用户输入："帮我分析一下这句话的意图：我要投诉信用卡盗刷"
    ↓
LLM 推理：需要调用 skill_tool 进行意图识别
    ↓
Agent 调用工具：skill_tool_wrapper("execskill", "intent-recognition '我要投诉信用卡盗刷'")
    ↓
HTTP API 调用：POST /skill-tool
    ↓
MagicSkills 执行技能：intent_recognition.py "我要投诉信用卡盗刷"
    ↓
技能返回结果：{
  "intents": [...],
  "primary_intent": "consumer_protection",
  "reasoning": "..."
}
    ↓
Agent 接收结果并生成回答
```

### 4.4 Agent 测试场景

**场景 1：意图识别**

```python
result = agent.invoke({
    "messages": [("user", "帮我分析一下这句话的意图：我要投诉信用卡盗刷")]
})

# Agent 自动调用 skill_tool_wrapper
# 工具调用：execskill intent-recognition "我要投诉信用卡盗刷"
# LLM 根据结果生成回答
```

**场景 2：技能查询**

```python
result = agent.invoke({
    "messages": [("user", "有哪些可以用的技能？")]
})

# Agent 自动调用 skill_tool_wrapper
# 工具调用：listskill
# 返回技能列表
```

### 4.5 为什么选择 HTTP API 集成？

**方案对比：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| **HTTP API 集成**（当前方案） | - API 独立部署，易于扩展<br>- 支持远程调用<br>- 多环境部署友好<br>- 前端/其他系统可直接调用 | - 需要启动 Flask 服务<br>- 网络调用开销（约 10-50ms） |
| **直接 Python API 集成** | - 调用速度快<br>- 无网络开销 | - 需要共享 Python 环境<br>- 部署复杂<br>- 不支持远程调用 |

**选择 HTTP API 的原因：**

1. **多环境部署友好**：MagicSkills API 可在不同环境中运行，Agent 可本地或远程调用
2. **易于扩展**：前端 UI、其他服务可通过 HTTP API 调用技能
3. **解耦设计**：MagicSkills 和 Agent 可独立部署和升级

### 4.6 HTTP API 服务端实现

**magicskills_api_v2_docker.py 关键接口：**

```python
@app.route('/skill-tool', methods=['POST'])
def skill_tool_api():
    """
    统一的 skill-tool 接口（兼容 CLI）

    Body:
    {
        "action": "listskill | readskill | execskill",
        "arg": "参数",
        "name": "集合名称"  // 可选，默认 Allskills
    }
    """
    data = request.json
    action = data['action']
    arg = data.get('arg', '')
    name = data.get('name', 'Allskills')

    try:
        if name == 'Allskills':
            skills_obj = ALL_SKILLS()
        else:
            skills_obj = REGISTRY.get_skills(name)

        result = skill_tool(skills_obj, action, arg)

        return jsonify({
            "success": True,
            "action": action,
            "result": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
```

---

## 5. 总结与展望

### 5.1 核心技术总结

| 技术 | 实现方式 | 优势 |
|------|----------|------|
| **MagicSkills 技能管理** | SKILL.md frontmatter + Skills 扫描 | 标准化技能定义，自动发现注册 |
| **Intent-recognition 技能** | LLM 驱动（DashScope qwen3-max） | 语义优先，多意图识别，可解释性强 |
| **技能注册机制** | Skills(path) → 扫描 SKILL.md → 解析 frontmatter → 创建 Skill 对象 | 自动化注册，无需手动配置 |
| **LangChain 集成** | HTTP API 包装 skill_tool + ReAct Agent | 解耦设计，易于扩展和部署 |

### 5.2 关键创新点

1. **LLM 驱动的意图识别**
   - 从关键词计数升级到语义理解
   - 识别关键词权重而非数量
   - 提供识别理由（reasoning）增强可解释性

2. **技能发现机制优化**
   - 主动初始化 Skills 实例
   - 解决 skills_count=0 问题
   - 确保技能在模块加载时就注册

3. **HTTP API 集成方案**
   - MagicSkills 独立部署为 HTTP 服务
   - LangChain Agent 通过 HTTP API 调用技能
   - 前端、其他服务可直接访问 API

### 5.3 后续优化方向

#### 技能扩展

- 添加更多银行金融场景技能
  - 客户画像分析技能
  - 智能问答技能
  - 知识库检索技能

#### LangChain 深度集成

- 直接 Python API 集成方案（无 HTTP 开销）
- 多 Agent 协作（不同技能由不同 Agent 负责）
- 技能链式调用（多个技能组合完成复杂任务）

#### 部署优化

- 技能市场（技能仓库，动态安装）
- 前端 UI（可视化技能管理和调用）
- 多环境支持（本地、服务器、云端）

### 5.4 技术栈总结

| 类别 | 技术 |
|------|------|
| **技能管理框架** | MagicSkills（GitHub: Narwhal-Lab/MagicSkills） |
| **意图识别** | LLM（DashScope qwen3-max） + LangChain |
| **Agent 框架** | LangGraph（ReAct Agent） |
| **HTTP API** | Flask |
| **Python 环境** | Python 3.10+ |

---

## 附录

### A. MagicSkills Python API 完整列表

```python
from magicskills import (
    # 技能查询
    listskill,      # 列出所有技能
    readskill,      # 读取技能文档（SKILL.md）
    showskill,      # 显示技能详情

    # 技能执行
    execskill,      # 执行技能命令

    # 技能管理
    addskill,       # 添加技能到集合
    deleteskill,    # 删除技能
    install,        # 安装技能（从 GitHub 或本地）

    # 集合管理
    addskills,      # 创建技能集合
    deleteskills,   # 删除集合
    listskills,     # 列出所有集合

    # 集合同步
    syncskills,     # 同步集合到 AGENTS.md

    # 注册表管理
    loadskills,     # 从磁盘加载注册表
    saveskills,     # 保存注册表到磁盘

    # 描述更新
    change_tool_description,   # 更新工具描述
    change_cli_description,    # 更新 CLI 描述

    # 统一接口
    skill_tool,     # 统一技能调用接口

    # 核心对象
    Skills,         # 技能集合类
    REGISTRY,       # 全局注册表
    ALL_SKILLS,     # 默认 Allskills 集合函数
)
```

### B. HTTP API 完整接口列表

| 端点 | 方法 | 功能 |
|------|------|------|
| `/` | GET | API 首页（服务信息） |
| `/health` | GET | 健康检查 |
| `/skills` | GET | 列出所有技能 |
| `/skills/<name>` | GET | 获取技能详情 |
| `/skills/<name>/content` | GET | 读取技能文档（SKILL.md） |
| `/skills/search` | POST | 搜索技能 |
| `/skills/execute` | POST | 执行技能命令 |
| `/collections` | GET | 列出所有集合 |
| `/collections/<name>` | GET | 获取集合详情 |
| `/collections/create` | POST | 创建集合 |
| `/collections/<name>/sync` | POST | 同步集合到 AGENTS.md |
| `/collections/<name>` | DELETE | 删除集合 |
| `/skill-tool` | POST | 统一技能调用接口 |

### C. 测试案例清单

| 测试场景 | 输入文本 | 期望主意图 | 验证点 |
|----------|----------|------------|--------|
| 语义优先 | "我要投诉信用卡盗刷" | `consumer_protection` | LLM 识别"投诉"权重高于"信用卡" |
| 单意图精确识别 | "查询上个月的账户流水明细" | `transaction_analysis` | 流水分析意图准确识别 |
| 零售贷款业务 | "我想查询信用卡额度" | `retail_loan_card` | 信用卡业务意图 |
| 多意图识别 | "我想申请信用卡，并了解信贷政策" | 多意图 | 识别多个意图并推荐主意图 |
| 无法识别 | "今天天气怎么样" | `unknown` | 不在预定义意图中 |

---

**文档版本：** v1.0
**最后更新：** 2026-04-13
**作者：** MagicSkills + LangChain Agent 项目团队