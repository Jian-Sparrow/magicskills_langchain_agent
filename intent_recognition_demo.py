#!/usr/bin/env python3
"""
MagicSkills + Intent Recognition Demo

演示 LangGraph Agent 通过 skill_tool 调用 MagicSkills（包括 intent-recognition）
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

# MagicSkills API 地址（容器内部）
# Docker容器内API运行在5000端口
API_BASE = "http://localhost:5001"  # 容器内部API
# 主机调用: API_BASE = "http://localhost:5002"

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