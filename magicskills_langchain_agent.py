#!/usr/bin/env python3
"""
MagicSkills + LangChain 集成脚本（DeepSeek 配置）- 使用 LangGraph

用法:
    sudo /root/miniforge3/envs/magicskills/bin/python3 magicskills_langchain_agent.py "有哪些处理 PDF 的技能？"
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
