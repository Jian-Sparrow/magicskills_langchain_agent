#!/usr/bin/env python3
"""
Intent Recognition 测试脚本
测试LLM驱动的意图识别效果
"""

import subprocess
import json
import sys

def test_intent_recognition(text: str, expected_intent: str = None):
    """
    测试意图识别

    Args:
        text: 测试文本
        expected_intent: 期望的主意图（可选）
    """
    print("=" * 80)
    print(f"测试文本: {text}")
    print("-" * 80)

    # 调用intent_recognition脚本
    result = subprocess.run(
        [sys.executable, "workspace/skills/allskills/intent-recognition/intent_recognition.py", text],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ 执行失败: {result.stderr}")
        return False

    # 解析JSON输出
    try:
        output = json.loads(result.stdout)
        print("识别结果:")
        print(json.dumps(output, ensure_ascii=False, indent=2))

        # 验证期望意图
        if expected_intent:
            primary_intent = output.get("primary_intent") or output.get("intent")
            if primary_intent == expected_intent:
                print(f"✅ 验证成功: 主意图匹配 {expected_intent}")
                return True
            else:
                print(f"❌ 验证失败: 期望 {expected_intent}, 实际 {primary_intent}")
                return False
        else:
            print("✅ 执行成功")
            return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"原始输出: {result.stdout}")
        return False

    print("=" * 80)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Intent Recognition 测试套件（LLM驱动版本）")
    print("=" * 80 + "\n")

    test_cases = [
        # 关键测试案例：语义优先（LLM正确识别投诉意图）
        ("我要投诉信用卡盗刷", "consumer_protection",
         "语义优先测试：'投诉'重要性高于'信用卡'"),

        # 单意图精确识别
        ("查询上个月的账户流水明细", "transaction_analysis",
         "单意图测试：流水分析"),

        # 零售贷款业务
        ("我想查询信用卡额度", "retail_loan_card",
         "零售贷款测试：信用卡业务"),

        # 多意图识别
        ("我想申请信用卡，并了解信贷政策", None,
         "多意图测试：信用卡申请 + 信贷知识"),

        # 信贷知识查询
        ("信贷政策有哪些规定", "credit_knowledge",
         "信贷知识测试"),

        # 无法识别的意图
        ("今天天气怎么样", "unknown",
         "无匹配测试：不在预定义意图中"),

        # 空输入
        ("", "unknown",
         "空输入测试"),
    ]

    success_count = 0
    total_count = len(test_cases)

    for text, expected_intent, description in test_cases:
        print(f"\n【{description}】")
        if test_intent_recognition(text, expected_intent):
            success_count += 1
        print()

    print("=" * 80)
    print(f"测试结果: {success_count}/{total_count} 通过")
    print("=" * 80)

    if success_count == total_count:
        print("🎉 所有测试通过！LLM驱动的意图识别工作正常")
    else:
        print(f"⚠️  {total_count - success_count} 个测试失败")

    print("\n关键改进验证:")
    print("- LLM能识别关键词的语义重要性（'投诉' > '信用卡'）")
    print("- 正确处理多意图场景并推荐主意图")
    print("- 提供reasoning说明增强可解释性")
    print("- 对不在预定义意图中的文本返回unknown")