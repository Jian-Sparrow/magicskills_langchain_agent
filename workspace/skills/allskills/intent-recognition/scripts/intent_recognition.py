#!/usr/bin/env python3
"""Intent Recognition Skill - 银行金融场景意图识别（LLM驱动）"""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 加载环境变量
load_dotenv(Path.home() / ".env")

# 意图类别定义
INTENT_CATEGORIES = {
    "retail_loan_card": {
        "name": "零售贷款与信用卡",
        "description": "零售条线，零售贷款与信用卡业务相关内容",
        "keywords": ["贷款", "信用卡", "房贷", "车贷", "消费贷", "额度", "利率", "还款", "分期", "逾期", "催收", "申卡", "用卡"]
    },
    "consumer_protection": {
        "name": "消保坐席",
        "description": "投诉专席客服处理客诉，智能助手赋能话术查询和授权",
        "keywords": ["投诉", "客诉", "维权", "申诉", "投诉专席", "话术", "授权", "处理投诉", "投诉处理", "消保", "消费者保护"]
    },
    "retail_analysis": {
        "name": "零售经营分析",
        "description": "零售业务的经营分析相关",
        "keywords": ["经营分析", "业绩", "指标", "数据分析", "报表", "零售业务", "业务分析", "经营数据", "分析报告"]
    },
    "wealth_party_building": {
        "name": "南银理财党建",
        "description": "理财产品的党建相关内容",
        "keywords": ["南银理财", "党建", "理财产品", "党建活动", "党组织", "理财党建"]
    },
    "credit_knowledge": {
        "name": "信贷知识",
        "description": "信贷相关的知识查询",
        "keywords": ["信贷", "信贷政策", "信贷流程", "信贷知识", "信贷业务", "贷款知识", "信贷制度"]
    },
    "transaction_analysis": {
        "name": "流水分析",
        "description": "账户流水分析",
        "keywords": ["流水", "账户流水", "流水分析", "流水查询", "账单", "交易记录", "资金流水", "流水明细"]
    },
    "quarterly_summary": {
        "name": "综合部各部门季度材料总结",
        "description": "综合部门的季度材料汇总",
        "keywords": ["综合部", "季度材料", "季度总结", "材料总结", "部门总结", "季度报告", "综合部门"]
    },
    "yunshuantong": {
        "name": "云算通财资产品",
        "description": "云算通财资产品相关",
        "keywords": ["云算通", "财资产品", "云算通产品", "财资", "资金管理"]
    }
}


def create_intent_prompt(text: str) -> str:
    """
    构建意图识别的Prompt

    Args:
        text: 用户输入文本

    Returns:
        完整的prompt字符串
    """
    # 构建意图类别描述
    intent_desc = "\n".join([
        f"- {intent_id}: {info['name']} - {info['description']}\n  关键词提示: {', '.join(info['keywords'][:5])}"
        for intent_id, info in INTENT_CATEGORIES.items()
    ])

    prompt = f"""你是一个专业的银行金融场景意图识别专家。请分析以下用户文本，识别其意图并返回结构化的JSON结果。

# 预定义意图类别体系

{intent_desc}

# 输出格式要求

请严格按照以下JSON格式输出（不要输出其他任何文字说明）：

单意图输出格式示例：
{{
  "intent": "retail_loan_card",
  "intent_name": "零售贷款与信用卡",
  "confidence": 0.85,
  "keywords": ["信用卡", "额度"],
  "matched_category": "关键词匹配",
  "reasoning": "识别理由说明"
}}

多意图输出格式示例（当文本包含多个明确意图时）：
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

无法识别意图时：
{{
  "intent": "unknown",
  "confidence": 0,
  "keywords": [],
  "reason": "无法匹配预定义意图类别"
}}

# 识别原则

1. 语义优先：优先考虑文本的语义含义，而不是关键词数量
2. 权重判断：某些关键词语义重要性更高（如投诉比信用卡更明确表示意图）
3. 置信度计算：高置信度0.8-1.0表示语义明确关键词清晰，中置信度0.5-0.8表示意图倾向明确但关键词较少，低置信度小于0.5表示意图模糊
4. 多意图判断：文本包含多个明确且独立的意图时返回多意图结果
5. 主意图选择：多意图场景中，选择语义最明确或用户最关注的意图作为primary_intent

# 用户输入文本

{text}

# 请输出意图识别结果（仅输出JSON格式，不要其他文字）"""
    return prompt


def recognize_intent(text: str) -> dict:
    """
    意图识别函数（向后兼容别名）

    Args:
        text: 用户输入文本

    Returns:
        结构化意图识别结果（JSON dict）
    """
    return recognize_intent_with_llm(text)


def recognize_intent_with_llm(text: str) -> dict:
    """
    使用LLM进行意图识别

    Args:
        text: 用户输入文本

    Returns:
        结构化意图识别结果（JSON dict）
    """
    # 输入验证
    if not text or len(text.strip()) == 0:
        return {
            "intent": "unknown",
            "confidence": 0,
            "keywords": [],
            "reason": "文本为空"
        }

    # 验证环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL")

    if not all([api_key, base_url, model]):
        return {
            "intent": "unknown",
            "confidence": 0,
            "keywords": [],
            "reason": "缺少必要的API配置（OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL）"
        }

    try:
        # 初始化LLM
        llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            api_key=api_key,
            temperature=0.0  # 低温度保证输出稳定性
        )

        # 构建prompt
        prompt = create_intent_prompt(text)

        # 调用LLM
        response = llm.invoke([HumanMessage(content=prompt)])

        # 提取JSON结果
        response_text = response.content.strip()

        # 尝试解析JSON
        try:
            # 如果LLM输出包含markdown代码块，提取JSON部分
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
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
                    "reason": f"LLM返回格式错误: {response_text}"
                }

        except json.JSONDecodeError as e:
            return {
                "intent": "unknown",
                "confidence": 0,
                "keywords": [],
                "reason": f"JSON解析失败: {str(e)}",
                "raw_response": response_text
            }

    except Exception as e:
        return {
            "intent": "unknown",
            "confidence": 0,
            "keywords": [],
            "reason": f"LLM调用失败: {str(e)}"
        }


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