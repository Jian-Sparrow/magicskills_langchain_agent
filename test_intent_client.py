#!/usr/bin/env python3
"""
意图识别客户端 - Docker HTTP API调用示例
演示如何通过HTTP API调用意图识别功能
"""

import requests
import json
import sys

class IntentRecognitionClient:
    """意图识别客户端"""

    def __init__(self, base_url="http://localhost:5002"):
        self.base_url = base_url
        self.execute_url = f"{base_url}/skills/execute"

    def recognize(self, text):
        """
        识别文本意图

        Args:
            text: 待识别的文本

        Returns:
            dict: 意图识别结果
        """
        command = f"python /app/workspace/skills/allskills/intent-recognition/scripts/intent_recognition.py \"{text}\""

        try:
            response = requests.post(
                self.execute_url,
                json={
                    "command": command,
                    "shell": True,
                    "timeout": 30
                },
                timeout=35  # HTTP请求超时略长于命令超时
            )

            # 检查HTTP状态码
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP错误: {response.status_code}"
                }

            result = response.json()

            if result.get('success'):
                # 解析stdout中的JSON结果
                intent_data = json.loads(result['stdout'])
                return {
                    "success": True,
                    "data": intent_data
                }
            else:
                return {
                    "success": False,
                    "error": result.get('stderr', 'Unknown error')
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "请求超时"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"网络请求失败: {str(e)}"
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON解析失败: {str(e)}"
            }

    def print_result(self, result):
        """打印意图识别结果"""
        if not result.get('success'):
            print(f"❌ 错误: {result['error']}")
            return

        data = result['data']

        # 单意图情况
        if 'intent' in data:
            print(f"✅ 意图: {data['intent_name']}")
            print(f"   Intent ID: {data['intent']}")
            print(f"   置信度: {data['confidence']:.2%}")
            print(f"   关键词: {', '.join(data['keywords'])}")
            if 'reasoning' in data:
                print(f"   理由: {data['reasoning']}")

        # 多意图情况
        elif 'intents' in data:
            print(f"✅ 识别到 {len(data['intents'])} 个意图:")
            print(f"   主要意图: {data['primary_intent']}")
            print()
            for i, intent in enumerate(data['intents'], 1):
                print(f"   意图{i}: {intent['intent_name']}")
                print(f"      Intent ID: {intent['intent']}")
                print(f"      置信度: {intent['confidence']:.2%}")
                print(f"      关键词: {', '.join(intent['keywords'])}")
            print()
            print(f"   推理: {data['reasoning']}")

        # 模糊意图情况
        elif data.get('intent') == 'uncertain':
            print(f"⚠️  意图模糊 (置信度: {data['confidence']:.2%})")
            print(f"   关键词: {', '.join(data['keywords'])}")
            print()
            print("   建议:")
            for suggestion in data['suggestions']:
                print(f"      - {suggestion['reason']}")
            print()
            print("   需要更多信息")

        # 未知意图情况
        elif data.get('intent') == 'unknown':
            print(f"❌ 无法识别意图")
            print(f"   理由: {data.get('reason', '未包含预定义意图关键词')}")

        else:
            print(f"❓ 未知结果格式: {data}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print(f"  {sys.argv[0]} \"待识别的文本\"")
        print()
        print("示例:")
        print(f"  {sys.argv[0]} \"我要投诉信用卡盗刷问题\"")
        print(f"  {sys.argv[0]} \"查询上个月的账户流水明细\"")
        print(f"  {sys.argv[0]} \"我想申请信用卡\"")
        sys.exit(1)

    text = sys.argv[1]

    print("=" * 60)
    print("意图识别客户端 - Docker HTTP API")
    print("=" * 60)
    print(f"服务地址: http://localhost:5002")
    print(f"待识别文本: {text}")
    print("=" * 60)
    print()

    # 创建客户端
    client = IntentRecognitionClient()

    # 执行意图识别
    print("正在识别意图...")
    result = client.recognize(text)

    # 打印结果
    print()
    client.print_result(result)
    print()
    print("=" * 60)

    # 返回原始JSON（用于调试）
    if '--json' in sys.argv:
        print()
        print("原始JSON结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()