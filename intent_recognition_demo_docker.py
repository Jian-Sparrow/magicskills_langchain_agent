#!/usr/bin/env python3
"""
Intent Recognition Demo - Docker Version
使用Docker容器中的MagicSkills API（端口5002）
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import requests
import json

# 加载环境变量
load_dotenv(Path.home() / ".env")

# 验证环境变量
required_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"❌ 缺少环境变量：{', '.join(missing_vars)}")
    sys.exit(1)

print("=" * 60)
print("Intent Recognition Demo (Docker API)")
print("=" * 60)
print(f"LLM Model: {os.getenv('OPENAI_MODEL')}")
print(f"LLM Base URL: {os.getenv('OPENAI_BASE_URL')}")
print(f"API Endpoint: http://localhost:5002")
print()

# Docker API地址（5002端口）
API_BASE = "http://localhost:5002"

@tool
def execute_intent_recognition(text: str) -> str:
    """
    执行意图识别。输入待识别的文本，返回意图分类结果。

    参数:
    - text: 待识别的用户文本

    示例:
    - "我要投诉信用卡盗刷问题"
    - "查询上个月的账户流水明细"
    """
    try:
        # 通过Docker API执行意图识别脚本
        response = requests.post(
            f"{API_BASE}/skills/execute",
            json={
                "command": f"python /app/workspace/skills/allskills/intent-recognition/scripts/intent_recognition.py \"{text}\"",
                "shell": True,
                "timeout": 30
            },
            timeout=35
        )

        if response.status_code != 200:
            return f"HTTP错误: {response.status_code}"

        result = response.json()

        if not result.get('success'):
            return f"执行失败: {result.get('stderr', 'Unknown error')}"

        # 解析意图识别结果
        intent_data = json.loads(result['stdout'])

        # 格式化输出
        if 'intents' in intent_data:
            output = f"识别到 {len(intent_data['intents'])} 个意图:\n"
            for i, intent in enumerate(intent_data['intents'], 1):
                output += f"  {i}. {intent['intent_name']} (置信度: {intent['confidence']:.0%})\n"
            output += f"主意图: {intent_data['primary_intent']}\n"
            output += f"理由: {intent_data['reasoning']}"
            return output
        elif 'intent' in intent_data:
            return f"意图: {intent_data['intent_name']} (置信度: {intent_data['confidence']:.0%})"
        else:
            return f"结果: {json.dumps(intent_data, ensure_ascii=False)}"

    except requests.exceptions.Timeout:
        return "请求超时"
    except Exception as e:
        return f"错误: {str(e)}"

@tool
def list_available_skills() -> str:
    """列出所有可用的MagicSkills技能"""
    try:
        response = requests.get(f"{API_BASE}/skills", timeout=10)
        data = response.json()
        skills = [s['name'] for s in data['skills']]
        return f"可用技能 ({data['count']}): {', '.join(skills)}"
    except Exception as e:
        return f"查询失败: {str(e)}"

# 创建工具列表
tools = [execute_intent_recognition, list_available_skills]

# 初始化 LLM
print("[初始化] 创建 LLM...")
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.0
)
print("✅ LLM 创建成功")

# 创建 Agent
print("[初始化] 创建 Agent...")
agent = create_react_agent(llm, tools)
print("✅ Agent 创建成功")
print()

def run_demo(prompt: str, title: str):
    """运行演示场景"""
    print("=" * 60)
    print(f"演示场景: {title}")
    print("=" * 60)
    print(f"用户输入: {prompt}\n")

    # 调用 Agent
    result = agent.invoke({"messages": [("user", prompt)]})

    # 显示结果
    final_message = result["messages"][-1]
    print("Agent 回答:")
    print(final_message.content)
    print("=" * 60)
    print()

if __name__ == "__main__":
    # 场景1: 意图识别
    run_demo(
        "请帮我识别这句话的意图：我要投诉信用卡盗刷问题",
        "意图识别 - 投诉场景"
    )

    # 场景2: 另一个意图识别示例
    run_demo(
        "分析意图：查询上个月的账户流水明细",
        "意图识别 - 查询场景"
    )

    # 场景3: 多意图识别
    run_demo(
        "识别意图：我想申请信用卡，并了解信贷政策",
        "意图识别 - 多意图场景"
    )

    # 场景4: 查询可用技能
    run_demo(
        "有哪些可用的技能？",
        "技能查询"
    )

    print("=" * 60)
    print("✅ Demo完成!")
    print("=" * 60)
    print("\n提示:")
    print("- Docker API地址: http://localhost:5002")
    print("- 意图识别脚本路径: scripts/intent_recognition.py")
    print("- 支持8个银行金融意图类别")
    print("=" * 60)