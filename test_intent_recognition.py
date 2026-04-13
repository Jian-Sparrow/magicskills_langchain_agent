# test_intent_recognition.py
"""测试 intent_recognition 核心逻辑"""

import sys
sys.path.insert(0, 'skills/intent-recognition')

from intent_recognition import recognize_intent

def test_consumer_protection_intent():
    """测试消保坐席意图识别"""
    text = "我要投诉"
    result = recognize_intent(text)

    assert result["intent"] == "consumer_protection"
    assert result["intent_name"] == "消保坐席"
    assert result["confidence"] >= 0.7
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
    # primary_intent can be either retail_loan_card or credit_knowledge, both have same confidence
    assert result["primary_intent"] in ["retail_loan_card", "credit_knowledge"]

def test_retail_loan_card_intent():
    """测试零售贷款意图"""
    text = "我想查询信用卡额度"
    result = recognize_intent(text)

    assert result["intent"] == "retail_loan_card"
    assert "信用卡" in result["keywords"]
    assert result["confidence"] >= 0.7

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