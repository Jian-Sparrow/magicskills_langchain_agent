# Intent Recognition Demo 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 验证 LangGraph Agent + MagicSkills HTTP API + intent-recognition skill 的集成可行性

**Architecture:** LangGraph ReAct Agent 通过 HTTP requests 调用 MagicSkills API（包括 intent-recognition skill），实现意图识别和技能查询两个测试场景。Demo 在本地运行，MagicSkills API 服务在本地或远程服务器运行。

**Tech Stack:** LangGraph, MagicSkills HTTP API, DeepSeek API, Python 3.10, requests

**Environment Setup:**
- Demo 脚本在本地 macOS 运行
- MagicSkills API 服务可选择：
  - 方式 A：本地运行 `magicskills_api_v2.py`（需先安装 magicskills Python 包）
  - 方式 B：远程服务器运行（Aliyun ECS），通过 HTTP API 调用
- 本 demo 使用**方式 A**（本地 API），如需远程请修改 API_BASE URL

---

## 文件结构规划

**新增文件：**
- `skills/intent-recognition/intent_recognition.py` - 意图识别核心实现（关键词匹配）
- `skills/intent-recognition/requirements.txt` - Skill 依赖清单
- `skills/intent-recognition/SKILL.md` - Skill 规范文档（复制）
- `intent_recognition_demo.py` - 主 demo 脚本（Agent + 测试场景）
- `test_intent_recognition.py` - intent-recognition 单元测试

**职责划分：**
- `intent_recognition.py`: 纯意图识别逻辑，无 Agent 依赖，可独立测试
- `intent_recognition_demo.py`: Agent 构建 + skill_tool 包装 + 场景测试
- `test_intent_recognition.py`: 验证意图识别逻辑正确性

---

## Task 0: 环境准备（必须先完成）

**Files:**
- None（环境验证）

**Prerequisites Check:**

- [ ] **Step 1: 验证 DeepSeek API 配置**

```bash
cat ~/.env | grep OPENAI
```

预期：应显示 `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`

- [ ] **Step 2: 验证依赖包已安装**

```bash
python -c "from langchain_openai import ChatOpenAI; from langgraph.prebuilt import create_react_agent; import requests; print('✅ 依赖已安装')"
```

如果失败，安装依赖：
```bash
pip install langchain-openai langgraph requests python-dotenv
```

- [ ] **Step 3: 启动 MagicSkills API 服务**

**方式 A（本地 API - 推荐）：**
```bash
# 需要先确保 magicskills_api_v2.py 可运行
# 如果本地有 magicskills Python 包：
nohup python magicskills_api_v2.py > /tmp/magicskills_api.log 2>&1 &
sleep 3
curl http://localhost:5000/health
```

预期：返回 `{"status": "ok", "skills_count": ...}`

**方式 B（远程 API - 可选）：**
```bash
# 修改 intent_recognition_demo.py 中的 API_BASE 为远程服务器地址
# 例如：API_BASE = "http://your-server-ip:5000"
curl http://your-server-ip:5000/health
```

- [ ] **Step 4: 验证 MagicSkills API 可访问**

```bash
curl http://localhost:5000/skills
```

预期：返回技能列表 JSON

---

## Task 1: 创建 skill 目录结构

**Files:**
- Create: `skills/intent-recognition/`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p skills/intent-recognition
```

验证：`ls -la skills/intent-recognition/` 应显示空目录

---

## Task 2: 实现 intent_recognition.py 核心逻辑

**Files:**
- Create: `skills/intent-recognition/intent_recognition.py`
- Create: `test_intent_recognition.py`

**遵循 TDD：先写测试，再实现**

- [ ] **Step 1: 创建测试文件骨架**

```python
# test_intent_recognition.py
"""测试 intent_recognition 核心逻辑"""

import sys
sys.path.insert(0, 'skills/intent-recognition')

from intent_recognition import recognize_intent

def test_consumer_protection_intent():
    """测试消保坐席意图识别"""
    text = "我要投诉信用卡盗刷"
    result = recognize_intent(text)

    assert result["intent"] == "consumer_protection"
    assert result["intent_name"] == "消保坐席"
    assert result["confidence"] > 0.8
    assert "投诉" in result["keywords"]
    assert result["matched_category"] in ["精确匹配", "关键词匹配"]

def test_unknown_intent():
    """测试无法识别的意图"""
    text = "今天天气怎么样"
    result = recognize_intent(text)

    assert result["intent"] == "unknown"
    assert result["confidence"] == 0

def test_multi_intent():
    """测试多意图场景"""
    text = "我想申请信用卡，并了解信贷政策"
    result = recognize_intent(text)

    assert "intents" in result
    assert len(result["intents"]) >= 2
    assert result["primary_intent"] in ["retail_loan_card", "credit_knowledge"]

if __name__ == "__main__":
    test_consumer_protection_intent()
    test_unknown_intent()
    test_multi_intent()
    print("✅ 所有测试通过")
```

- [ ] **Step 2: 运行测试验证失败**

```bash
python test_intent_recognition.py
```

预期：`ModuleNotFoundError: No module named 'intent_recognition'`

- [ ] **Step 3: 创建 intent_recognition.py 框架**

```python
#!/usr/bin/env python3
"""Intent Recognition Skill - 银行金融场景意图识别"""

import sys
import json

# 意图类别定义（从 SKILL.md 提取）
INTENT_CATEGORIES = {
    "retail_loan_card": {
        "name": "零售贷款与信用卡",
        "keywords": ["贷款", "信用卡", "房贷", "车贷", "消费贷", "额度", "利率", "还款", "分期", "逾期", "催收", "申卡", "用卡"]
    },
    "consumer_protection": {
        "name": "消保坐席",
        "keywords": ["投诉", "客诉", "维权", "申诉", "投诉专席", "话术", "授权", "处理投诉", "投诉处理", "消保", "消费者保护"]
    },
    "retail_analysis": {
        "name": "零售经营分析",
        "keywords": ["经营分析", "业绩", "指标", "数据分析", "报表", "零售业务", "业务分析", "经营数据", "分析报告"]
    },
    "wealth_party_building": {
        "name": "南银理财党建",
        "keywords": ["南银理财", "党建", "理财产品", "党建活动", "党组织", "理财党建"]
    },
    "credit_knowledge": {
        "name": "信贷知识",
        "keywords": ["信贷", "信贷政策", "信贷流程", "信贷知识", "信贷业务", "贷款知识", "信贷制度"]
    },
    "transaction_analysis": {
        "name": "流水分析",
        "keywords": ["流水", "账户流水", "流水分析", "流水查询", "账单", "交易记录", "资金流水", "流水明细"]
    },
    "quarterly_summary": {
        "name": "综合部各部门季度材料总结",
        "keywords": ["综合部", "季度材料", "季度总结", "材料总结", "部门总结", "季度报告", "综合部门"]
    },
    "yunshuantong": {
        "name": "云算通财资产品",
        "keywords": ["云算通", "财资产品", "云算通产品", "财资", "资金管理"]
    }
}

def recognize_intent(text: str) -> dict:
    """
    核心意图识别逻辑（关键词匹配）

    Args:
        text: 用户输入文本

    Returns:
        结构化意图识别结果（JSON dict）
    """
    # TODO: 实现逻辑
    pass

if __name__ == "__main__":
    # 命令行接口
    pass
```

- [ ] **Step 4: 运行测试验证基础结构**

```bash
python test_intent_recognition.py
```

预期：`AttributeError: 'NoneType' object has no attribute '__getitem__'`（recognize_intent 返回 None）

- [ ] **Step 5: 实现 recognize_intent 核心逻辑**

```python
def recognize_intent(text: str) -> dict:
    """
    核心意图识别逻辑（关键词匹配）

    Args:
        text: 用户输入文本

    Returns:
        结构化意图识别结果（JSON dict）
    """
    if not text or len(text.strip()) == 0:
        return {
            "intent": "unknown",
            "confidence": 0,
            "keywords": [],
            "reason": "文本为空"
        }

    text_lower = text.lower()

    # 统计每个意图类别匹配的关键词
    matches = []
    for intent_id, intent_info in INTENT_CATEGORIES.items():
        matched_keywords = []
        for keyword in intent_info["keywords"]:
            if keyword.lower() in text_lower:
                matched_keywords.append(keyword)

        if matched_keywords:
            # 计算置信度：匹配关键词数 / 总关键词数
            confidence = len(matched_keywords) / len(intent_info["keywords"])
            matches.append({
                "intent": intent_id,
                "intent_name": intent_info["name"],
                "confidence": round(confidence, 2),
                "keywords": matched_keywords
            })

    # 无匹配
    if not matches:
        return {
            "intent": "unknown",
            "confidence": 0,
            "keywords": [],
            "reason": "未找到匹配关键词"
        }

    # 按置信度排序
    matches.sort(key=lambda x: x["confidence"], reverse=True)

    # 单意图场景（置信度 > 0.5）
    if matches[0]["confidence"] > 0.5:
        result = matches[0]
        # 确定匹配类别
        if result["confidence"] >= 0.8:
            result["matched_category"] = "精确匹配"
        else:
            result["matched_category"] = "关键词匹配"
        return result

    # 多意图场景（多个类别置信度相近）
    top_matches = [m for m in matches if m["confidence"] >= 0.3]
    if len(top_matches) >= 2:
        return {
            "intents": top_matches,
            "primary_intent": top_matches[0]["intent"],
            "reasoning": f"检测到 {len(top_matches)} 个可能意图"
        }

    # 模糊意图（置信度低）
    return {
        "intent": "uncertain",
        "confidence": matches[0]["confidence"],
        "keywords": matches[0]["keywords"],
        "suggestions": [
            {
                "intent": m["intent"],
                "reason": m["intent_name"]
            }
            for m in matches[:2]
        ]
    }
```

- [ ] **Step 6: 运行测试验证核心逻辑**

```bash
python test_intent_recognition.py
```

预期：`✅ 所有测试通过`

- [ ] **Step 7: 实现 __main__ 命令行接口**

```python
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "需要提供文本参数",
            "usage": "python intent_recognition.py \"文本内容\""
        }, ensure_ascii=False))
        sys.exit(1)

    text = sys.argv[1]
    result = recognize_intent(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

- [ ] **Step 8: 手动测试命令行接口**

```bash
python skills/intent-recognition/intent_recognition.py "我要投诉信用卡盗刷"
```

预期输出：
```json
{
  "intent": "consumer_protection",
  "intent_name": "消保坐席",
  "confidence": 0.27,
  "keywords": ["投诉", "信用卡", "盗刷"],
  "matched_category": "关键词匹配"
}
```

- [ ] **Step 9: 测试多意图场景**

```bash
python skills/intent-recognition/intent_recognition.py "我想申请信用卡，并了解信贷政策"
```

预期：返回包含 `intents` 列表的 JSON

- [ ] **Step 10: 测试 unknown 场景**

```bash
python skills/intent-recognition/intent_recognition.py "今天天气怎么样"
```

预期：`{"intent": "unknown", "confidence": 0}`

---

## Task 3: 创建 skill 依赖和规范文件

**Files:**
- Create: `skills/intent-recognition/requirements.txt`
- Create: `skills/intent-recognition/SKILL.md` (复制)

- [ ] **Step 1: 创建 requirements.txt**

```bash
cat > skills/intent-recognition/requirements.txt << 'EOF'
# Intent Recognition Skill Dependencies
# 无额外依赖，纯 Python 实现
EOF
```

- [ ] **Step 2: 复制 SKILL.md**

```bash
cp /Users/liujiansmac/.claude/skills/intent-recognition/SKILL.md \
   skills/intent-recognition/SKILL.md
```

验证：`ls -la skills/intent-recognition/` 应显示 3 个文件

---

## Task 4: 创建 intent_recognition_demo.py 基础结构

**Files:**
- Create: `intent_recognition_demo.py`

- [ ] **Step 1: 创建脚本骨架和导入**

```python
#!/usr/bin/env python3
"""
MagicSkills + Intent Recognition Demo

演示 LangGraph Agent 通过 skill_tool 调用 MagicSkills（包括 intent-recognition）
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(Path.home() / ".env")

# 验证环境变量
required_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL"]
for var in required_vars:
    if not os.getenv(var):
        print(f"❌ 缺少环境变量：{var}")
        sys.exit(1)

print("=" * 60)
print("MagicSkills + LangGraph Agent Demo")
print("=" * 60)
print(f"LLM Model: {os.getenv('OPENAI_MODEL')}")
print(f"LLM Base URL: {os.getenv('OPENAI_BASE_URL')}")
print()
```

- [ ] **Step 2: 运行骨架验证环境变量**

```bash
python intent_recognition_demo.py
```

预期：打印标题和配置信息，然后提示缺少 Agent 实现

---

## Task 5: 实现 skill_tool wrapper 和 Agent 初始化

**Files:**
- Modify: `intent_recognition_demo.py`

- [ ] **Step 1: 添加 LangGraph 导入**

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import requests
import json
```

**关键说明：** 使用 HTTP requests 调用 MagicSkills API，不直接导入 magicskills 模块。

- [ ] **Step 2: 定义 API 基础 URL**

```python
# MagicSkills API 地址
API_BASE = "http://localhost:5000"  # 本地 API
# 或远程 API: API_BASE = "http://your-server-ip:5000"
```

- [ ] **Step 3: 实现 skill_tool wrapper（HTTP API 版）**

```python
def _make_skill_tool(api_base: str):
    """
    通过 HTTP API 包装 MagicSkills skill_tool

    参考：现有 magicskills_langchain_agent.py 的工具定义
    """
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
```

- [ ] **Step 4: 修改 Agent 初始化代码**

```python
# 创建 tool（通过 HTTP API）
tools = [_make_skill_tool(API_BASE)]
print(f"Tools: {[t.name for t in tools]}")

# 初始化 LLM
print("[初始化] 创建 LLM...")
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.0
)
print("✅ LLM 创建成功")

# 创建 ReAct Agent
print("[初始化] 创建 Agent...")
agent = create_react_agent(llm, tools)
print("✅ Agent 创建成功")
print()
```

- [ ] **Step 5: 运行验证 Agent 初始化**

```bash
# 确保 MagicSkills API 正在运行
curl http://localhost:5000/health

# 运行 demo
python intent_recognition_demo.py
```

预期：成功创建 Agent，显示 "✅ Agent 创建成功"

**关键差异说明：**
- 本方案使用 HTTP API（requests）而非直接导入 magicskills 模块
- 与现有 `magicskills_langchain_agent.py` 保持一致
- 支持本地和远程 API 服务器

---

## Task 6: 实现测试场景和主函数

**Files:**
- Modify: `intent_recognition_demo.py`

- [ ] **Step 1: 定义测试场景函数**

```python
def run_scenario(prompt: str, scenario_name: str):
    """运行单个测试场景"""
    print("=" * 60)
    print(f"场景：{scenario_name}")
    print("=" * 60)
    print(f"用户输入：{prompt}\n")

    # 调用 Agent
    result = agent.invoke({"messages": [("user", prompt)]})

    # 提取最终回答
    final_message = result["messages"][-1]
    answer = final_message.content

    # 显示结果
    print("Agent 最终回答：")
    print(answer)
    print("=" * 60)
    print()

    return result
```

- [ ] **Step 2: 添加主函数**

```python
if __name__ == "__main__":
    # 场景 1：意图识别
    run_scenario(
        prompt="帮我分析一下这句话的意图：我要投诉信用卡盗刷",
        scenario_name="意图识别"
    )

    # 场景 2：技能查询
    run_scenario(
        prompt="有哪些可以用的技能？",
        scenario_name="技能查询"
    )

    print("=" * 60)
    print("✅ Demo 完成！")
    print("=" * 60)
```

- [ ] **Step 3: 运行完整 demo**

```bash
python intent_recognition_demo.py
```

预期：成功运行两个场景，Agent 返回正确答案

---

## Task 7: 优化输出格式（可选）

**Files:**
- Modify: `intent_recognition_demo.py`

- [ ] **Step 1: 增强输出显示（显示工具调用过程）**

在 `run_scenario` 函数中添加：

```python
def run_scenario(prompt: str, scenario_name: str):
    """运行单个测试场景"""
    print("=" * 60)
    print(f"场景：{scenario_name}")
    print("=" * 60)
    print(f"用户输入：{prompt}\n")

    result = agent.invoke({"messages": [("user", prompt)]})

    # 显示工具调用过程
    print("Agent 思考过程：")
    for i, msg in enumerate(result["messages"][1:-1]):  # 排除第一条用户消息和最后一条助手消息
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  [调用 {tc['name']}] args={tc['args']}")
        if msg.type == "tool":
            print(f"  [工具返回] {msg.content[:100]}...")  # 只显示前100字符
    print()

    # 显示最终回答
    final_message = result["messages"][-1]
    print("Agent 最终回答：")
    print(final_message.content)
    print("=" * 60)
    print()

    return result
```

- [ ] **Step 2: 运行优化后的 demo**

```bash
python intent_recognition_demo.py
```

预期：清晰显示 Agent 的思考过程和工具调用链

---

## Task 8: 创建完整测试验证

**Files:**
- Modify: `test_intent_recognition.py`

- [ ] **Step 1: 添加更多测试场景**

```python
def test_retail_loan_card_intent():
    """测试零售贷款意图"""
    text = "我想查询信用卡额度"
    result = recognize_intent(text)

    assert result["intent"] == "retail_loan_card"
    assert "信用卡" in result["keywords"]
    assert result["confidence"] > 0

def test_transaction_analysis_intent():
    """测试流水分析意图"""
    text = "查询上个月的账户流水明细"
    result = recognize_intent(text)

    assert result["intent"] == "transaction_analysis"
    assert "流水" in result["keywords"]

def test_empty_input():
    """测试空输入"""
    text = ""
    result = recognize_intent(text)

    assert result["intent"] == "unknown"
    assert result["reason"] == "文本为空"
```

- [ ] **Step 2: 更新测试运行器**

```python
if __name__ == "__main__":
    tests = [
        test_consumer_protection_intent,
        test_unknown_intent,
        test_multi_intent,
        test_retail_loan_card_intent,
        test_transaction_analysis_intent,
        test_empty_input
    ]

    for test in tests:
        test_name = test.__name__
        try:
            test()
            print(f"✅ {test_name} PASS")
        except AssertionError as e:
            print(f"❌ {test_name} FAIL: {str(e)}")
            raise
```

- [ ] **Step 3: 运行完整测试套件**

```bash
python test_intent_recognition.py
```

预期：所有 6 个测试通过

---

## Task 9: 文档和清理

**Files:**
- Create: `skills/intent-recognition/README.md` (可选)

- [ ] **Step 1: 创建 skill README**

```bash
cat > skills/intent-recognition/README.md << 'EOF'
# Intent Recognition Skill

银行金融场景意图识别 skill，用于 MagicSkills 系统。

## 功能

- 8 个预定义意图类别（银行金融业务场景）
- 关键词匹配 + 置信度计算
- 支持单意图、多意图、模糊意图场景

## 使用方式

### 作为 MagicSkills skill

```bash
# 通过 skill_tool 调用
magicskills skill-tool execskill intent-recognition "我要投诉信用卡盗刷"
```

### 独立运行

```bash
python intent_recognition.py "我要投诉信用卡盗刷"
```

## 测试

```bash
python test_intent_recognition.py
```

## 参考

- SKILL.md: 完整规范文档
EOF
```

- [ ] **Step 2: 验证所有文件完整性**

```bash
ls -la skills/intent-recognition/
ls -la *.py
```

预期：
- `skills/intent-recognition/` 包含 4 个文件（intent_recognition.py, requirements.txt, SKILL.md, README.md）
- 根目录包含 `intent_recognition_demo.py`, `test_intent_recognition.py`

---

## Task 10: 最终集成验证

**Files:**
- All created files

**前提条件：**
- MagicSkills API 服务正在运行（http://localhost:5000）
- intent-recognition skill 已安装到 MagicSkills 系统（通过 HTTP API 或 CLI）

**重要说明：**
- intent-recognition skill 需要先安装到 MagicSkills API 服务的技能目录
- 安装方式取决于 API 服务运行位置（本地或远程）
- 参考 spec 5.1 步骤 2 进行 skill 安装

- [ ] **Step 0: 安装 intent-recognition skill 到 MagicSkills 系统**

**如果 API 服务在本地运行：**
```bash
# 通过 HTTP API 安装（skill 文件需先准备好）
curl -X POST http://localhost:5000/skills/install \
  -H "Content-Type: application/json" \
  -d '{"source":"skills/intent-recognition","target_root":"skills/allskills"}'

# 验证安装
curl http://localhost:5000/skills | grep intent-recognition
```

**如果 API 服务在远程服务器：**
```bash
# 1. 复制 skill 文件到远程服务器
scp -r skills/intent-recognition user@server:/tmp/intent-recognition

# 2. 在远程服务器安装
ssh user@server "curl -X POST http://localhost:5000/skills/install -H 'Content-Type: application/json' -d '{\"source\":\"/tmp/intent-recognition\",\"target_root\":\"/home/admin/.openclaw/workspace/skills/allskills\"}'"

# 3. 验证
curl http://server-ip:5000/skills | grep intent-recognition
```

- [ ] **Step 1: 运行单元测试**

```bash
python test_intent_recognition.py
```

预期：所有测试通过

- [ ] **Step 2: 运行 demo 脚本**

```bash
# 确保 MagicSkills API 正在运行
curl http://localhost:5000/health

# 运行 demo
python intent_recognition_demo.py
```

预期：
- 场景 1：Agent 通过 skill_tool 调用 intent-recognition skill，返回意图识别结果
- 场景 2：Agent 通过 skill_tool 调用 listskill，返回技能列表

- [ ] **Step 3: 手动测试 skill 通过 HTTP API**

```bash
# 测试意图识别（通过 skill-tool API）
curl -X POST http://localhost:5000/skill-tool \
  -H "Content-Type: application/json" \
  -d '{"action":"execskill","arg":"intent-recognition \"我要投诉信用卡盗刷\"","name":"Allskills"}'

# 测试列出技能
curl -X POST http://localhost:5000/skill-tool \
  -H "Content-Type: application/json" \
  -d '{"action":"listskill","arg":"","name":"Allskills"}'
```

预期：返回正确的 JSON 格式结果

- [ ] **Step 4: 验证 Agent 工具调用日志**

查看 Agent 的完整输出，确认：
- Agent 正确调用 `skill_tool_wrapper`
- action 参数正确（listskill/readskill/execskill）
- arg 参数正确（skill 名称或命令）
- 返回结果正确解析

---

## 成功标准验证

**验证清单：**

- [ ] intent_recognition.py 实现 8 个意图类别关键词匹配
- [ ] recognize_intent() 返回正确的 JSON 结构
- [ ] 支持单意图、多意图、unknown 场景
- [ ] test_intent_recognition.py 包含至少 6 个测试场景并全部通过
- [ ] intent_recognition_demo.py 成功创建 LangGraph Agent
- [ ] skill_tool wrapper 通过 HTTP API 调用 MagicSkills API（不直接导入 magicskills）
- [ ] intent-recognition skill 已安装到 MagicSkills 系统（可通过 API 访问）
- [ ] 场景 1：Agent 成功调用 intent-recognition skill（通过 HTTP API）
- [ ] 场景 2：Agent 成功调用 listskill（通过 HTTP API）
- [ ] 所有文件结构完整（intent_recognition.py, requirements.txt, SKILL.md, README.md）

**关键差异：**
- 本计划使用 HTTP API 方式（requests），不依赖本地 magicskills Python 包
- 与现有 `magicskills_langchain_agent.py` 保持架构一致
- 支持本地和远程 MagicSkills API 服务器

---

## 参考文档

**Spec:** `docs/superpowers/specs/2026-04-10-intent-recognition-demo-design.md`

**官方示例：**
- [MagicSkills LangGraph Example](https://github.com/Narwhal-Lab/MagicSkills/tree/main/langgraph_example)
- [MagicSkills Python API](https://github.com/Narwhal-Lab/MagicSkills/blob/main/doc/python-api.zh-CN.md)

---

**计划完成日期：** 2026-04-10
**预估工作量：** 3-4 小时
**下一步：** 执行实施