# Docker部署与意图识别调用指南

## Docker部署

### 环境配置

项目根目录 `.env` 文件配置：

```bash
# API配置（阿里云通义千问）
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen3-max
```

### 启动Docker

```bash
# 启动容器
docker-compose up -d

# 查看容器状态
docker ps

# 查看日志
docker logs magicskills-all-in-one

# 健康检查
curl http://localhost:5002/health
```

### 端口映射

- 容器内部：5000
- 外部访问：5002

## 意图识别调用方法

### 方法1：通过HTTP API调用（推荐）

#### 1.1 执行意图识别脚本

```bash
curl -X POST http://localhost:5002/skills/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python /app/workspace/skills/allskills/intent-recognition/scripts/intent_recognition.py \"我要投诉信用卡盗刷问题\"",
    "shell": true,
    "timeout": 30
  }'
```

**返回结果：**

```json
{
  "success": true,
  "command": "...",
  "returncode": 0,
  "stdout": "{\n  \"intents\": [...],\n  \"primary_intent\": \"consumer_protection\",\n  \"reasoning\": \"...\"\n}",
  "stderr": ""
}
```

#### 1.2 使用Python解析stdout

```python
import requests
import json

# 发送请求
response = requests.post(
    'http://localhost:5002/skills/execute',
    json={
        "command": "python /app/workspace/skills/allskills/intent-recognition/scripts/intent_recognition.py \"查询上个月的账户流水明细\"",
        "shell": True,
        "timeout": 30
    }
)

# 解析结果
result = response.json()
if result['success']:
    intent_data = json.loads(result['stdout'])
    print(f"主要意图: {intent_data['primary_intent']}")
    print(f"置信度: {intent_data['intents'][0]['confidence']}")
```

### 方法2：在容器内直接执行

```bash
# 进入容器
docker exec -it magicskills-all-in-one bash

# 执行意图识别
python /app/workspace/skills/allskills/intent-recognition/scripts/intent_recognition.py "我要申请信用卡"
```

### 方法3：使用skill-tool统一接口

```bash
curl -X POST http://localhost:5002/skill-tool \
  -H "Content-Type: application/json" \
  -d '{
    "action": "execskill",
    "arg": "intent-recognition \"我要投诉信用卡盗刷\"",
    "name": "Allskills"
  }'
```

## API端点说明

### 核心端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/skills` | GET | 列出所有skills |
| `/skills/<name>` | GET | 获取skill详情 |
| `/skills/<name>/content` | GET | 读取SKILL.md内容 |
| `/skills/execute` | POST | **执行skill命令（推荐）** |
| `/skill-tool` | POST | 统一skill接口 |

### 查询端点

```bash
# 查看所有skills
curl http://localhost:5002/skills

# 查看intent-recognition skill详情
curl http://localhost:5002/skills/intent-recognition

# 查看SKILL.md内容
curl http://localhost:5002/skills/intent-recognition/content

# 搜索skills
curl -X POST http://localhost:5002/skills/search \
  -H "Content-Type: application/json" \
  -d '{"query": "intent"}'
```

## 意图识别输出格式

### 单意图输出

```json
{
  "intent": "retail_loan_card",
  "intent_name": "零售贷款与信用卡",
  "confidence": 0.85,
  "keywords": ["信用卡", "额度"],
  "matched_category": "精确匹配"
}
```

### 多意图输出

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
      "confidence": 0.78,
      "keywords": ["信用卡"]
    }
  ],
  "primary_intent": "consumer_protection",
  "reasoning": "用户明确表达'投诉'意图..."
}
```

### 模糊意图输出

```json
{
  "intent": "uncertain",
  "confidence": 0.4,
  "keywords": ["贷款", "利率"],
  "suggestions": [
    {
      "intent": "retail_loan_card",
      "reason": "贷款利率可能指向零售贷款产品咨询"
    },
    {
      "intent": "credit_knowledge",
      "reason": "贷款利率可能查询信贷政策知识"
    }
  ],
  "need_more_info": true
}
```

### 未知意图输出

```json
{
  "intent": "unknown",
  "confidence": 0,
  "keywords": [],
  "reason": "文本未包含任何预定义意图的关键词"
}
```

## 支持的意图类别

| Intent ID | Intent Name | Description | Keywords |
|-----------|-------------|-------------|----------|
| `retail_loan_card` | 零售贷款与信用卡 | 零售贷款与信用卡业务 | 贷款、信用卡、房贷、车贷、额度、利率、还款 |
| `consumer_protection` | 消保坐席 | 投诉专席客服 | 投诉、客诉、维权、申诉、话术、授权 |
| `retail_analysis` | 零售经营分析 | 零售业务经营分析 | 经营分析、业绩、指标、数据分析、报表 |
| `wealth_party_building` | 南银理财党建 | 理财产品党建 | 南银理财、党建、理财产品 |
| `credit_knowledge` | 信贷知识 | 信贷知识查询 | 信贷、信贷政策、信贷流程 |
| `transaction_analysis` | 流水分析 | 账户流水分析 | 流水、账户流水、流水查询、账单 |
| `quarterly_summary` | 综合部季度总结 | 综合部门季度材料 | 综合部、季度材料、季度总结 |
| `yunshuantong` | 云算通财资产品 | 云算通财资产品 | 云算通、财资产品、资金管理 |

## Python集成示例

### 完整的意图识别客户端

```python
import requests
import json

class IntentRecognitionClient:
    def __init__(self, base_url="http://localhost:5002"):
        self.base_url = base_url
        self.execute_url = f"{base_url}/skills/execute"

    def recognize(self, text):
        """识别文本意图"""
        command = f"python /app/workspace/skills/allskills/intent-recognition/scripts/intent_recognition.py \"{text}\""

        response = requests.post(
            self.execute_url,
            json={
                "command": command,
                "shell": True,
                "timeout": 30
            }
        )

        result = response.json()

        if result['success']:
            intent_data = json.loads(result['stdout'])
            return intent_data
        else:
            return {
                "error": result['stderr'],
                "success": False
            }

# 使用示例
client = IntentRecognitionClient()

# 测试1：投诉类文本
result1 = client.recognize("我要投诉信用卡盗刷问题")
print(f"主要意图: {result1['primary_intent']}")

# 测试2：查询类文本
result2 = client.recognize("查询上个月的账户流水明细")
print(f"意图: {result2['intent']}")

# 测试3：模糊文本
result3 = client.recognize("贷款利率怎么样")
print(f"建议: {result3['suggestions']}")
```

## 常见问题

### Q1: 容器启动失败？

```bash
# 查看容器日志
docker logs magicskills-all-in-one

# 检查.env配置
cat .env

# 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Q2: 意图识别超时？

调整timeout参数：

```bash
curl -X POST http://localhost:5002/skills/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "...",
    "shell": true,
    "timeout": 60  # 增加超时时间
  }'
```

### Q3: 如何更新意图类别？

修改 `workspace/skills/allskills/intent-recognition/scripts/intent_recognition.py` 中的 `INTENT_CATEGORIES`：

```python
INTENT_CATEGORIES = {
    # 添加新意图类别
    "new_intent": {
        "name": "新意图名称",
        "description": "意图描述",
        "keywords": ["关键词1", "关键词2"]
    }
}
```

然后重新构建容器：

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## 技术架构

### 容器内目录结构

```
/app/
├── magicskills_api_v2.py         # HTTP API服务
├── start.sh                      # 启动脚本
├── intent_recognition_demo.py    # Agent演示
├── test_intent_llm.py            # LLM测试
└── workspace/
    ├── AGENTS.md                 # Agents配置
    ├── skills/
    │   └── allskills/
    │       └── intent-recognition/
    │           ├── SKILL.md      # Skill定义
    │           └── scripts/      # **重构后的标准结构**
    │               ├── intent_recognition.py
    │               └── requirements.txt
    ├── logs/                     # 日志目录
    └── data/                     # 数据目录
```

### 依赖关系

- **HTTP API**: Flask + MagicSkills Python API
- **意图识别**: LangChain + ChatOpenAI (阿里云通义千问)
- **容器化**: Docker + docker-compose

## 下一步

- 集成到生产应用中
- 扩展意图类别
- 优化识别准确率
- 添加意图跟踪和分析

---

**注意**：所有示例中的localhost:5002都可以替换为实际的服务器IP地址用于远程访问。