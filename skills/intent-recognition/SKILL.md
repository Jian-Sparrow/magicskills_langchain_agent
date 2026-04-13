---
name: intent-recognition
description: 从用户文本中提取意图信息并进行分类。Trigger whenever user asks to identify intent, analyze requests, classify messages, or extract needs from text — any clear signal of intent recognition regardless of phrasing. Use this skill even when user doesn't explicitly say "intent recognition" but the task clearly involves understanding what someone wants or categorizing their request.
---

# Intent Recognition Skill

从文本中识别用户意图并分类到预定义业务类别。

## Quick Start

```
/intent-recognition "文本内容"
```

## Intent Categories (预定义意图体系)

银行金融业务场景的意图分类体系：

| Intent ID | Intent Name | Description | Keywords |
|-----------|-------------|-------------|----------|
| `retail_loan_card` | 零售贷款与信用卡 | 零售条线，零售贷款与信用卡业务相关内容 | 贷款、信用卡、房贷、车贷、消费贷、额度、利率、还款、分期、逾期、催收、申卡、用卡 |
| `consumer_protection` | 消保坐席 | 投诉专席客服处理客诉，智能助手赋能话术查询和授权 | 投诉、客诉、维权、申诉、投诉专席、话术、授权、处理投诉、投诉处理、消保、消费者保护 |
| `retail_analysis` | 零售经营分析 | 零售业务的经营分析相关 | 经营分析、业绩、指标、数据分析、报表、零售业务、业务分析、经营数据、分析报告 |
| `wealth_party_building` | 南银理财党建 | 理财产品的党建相关内容 | 南银理财、党建、理财产品、党建活动、党组织、理财党建 |
| `credit_knowledge` | 信贷知识 | 信贷相关的知识查询 | 信贷、信贷政策、信贷流程、信贷知识、信贷业务、贷款知识、信贷制度 |
| `transaction_analysis` | 流水分析 | 账户流水分析 | 流水、账户流水、流水分析、流水查询、账单、交易记录、资金流水、流水明细 |
| `quarterly_summary` | 综合部各部门季度材料总结 | 综合部门的季度材料汇总 | 综合部、季度材料、季度总结、材料总结、部门总结、季度报告、综合部门 |
| `yunshuantong` | 云算通财资产品 | 云算通财资产品相关 | 云算通、财资产品、云算通产品、财资、资金管理 |

## Recognition Logic

### Step 1: Text Analysis
分析输入文本，识别关键信息：
- 关键词提取
- 业务场景识别
- 上下文理解
- 隐含意图推断

### Step 2: Intent Matching
匹配到预定义意图类别：

**优先级规则：**
1. **精确匹配** - 文本明确提及某个业务类别（如"我要投诉"→消保坐席）
2. **关键词匹配** - 提取关键词映射到意图类别（如"信用卡额度"→零售贷款与信用卡）
3. **场景推断** - 根据业务场景推断意图（如"查询账户交易明细"→流水分析）
4. **默认分类** - 无法明确匹配时返回 `unknown`，建议用户补充信息

**匹配策略：**
- 单个意图：文本明确指向单一意图时，返回最高置信度的意图
- 多意图：文本包含多个意图时，返回所有匹配意图及其置信度
- 模糊意图：置信度低于阈值（<0.5）时返回 `uncertain` 并提供可能选项

### Step 3: Confidence Calculation
计算置信度（0-1）：
- **高置信度（0.8-1.0）**：明确关键词+业务场景清晰
- **中置信度（0.5-0.8）**：关键词匹配但场景不明确
- **低置信度（<0.5）**：关键词模糊或缺少上下文

### Step 4: Output Generation
生成结构化意图分类结果。

## Output Format

### Single Intent（单意图）
```json
{
  "intent": "retail_loan_card",
  "intent_name": "零售贷款与信用卡",
  "confidence": 0.85,
  "keywords": ["信用卡", "额度"],
  "matched_category": "精确匹配"
}
```

### Multiple Intents（多意图）
```json
{
  "intents": [
    {
      "intent": "retail_loan_card",
      "intent_name": "零售贷款与信用卡",
      "confidence": 0.75,
      "keywords": ["信用卡"],
      "matched_category": "关键词匹配"
    },
    {
      "intent": "transaction_analysis",
      "intent_name": "流水分析",
      "confidence": 0.65,
      "keywords": ["流水"],
      "matched_category": "关键词匹配"
    }
  ],
  "primary_intent": "retail_loan_card",
  "reasoning": "信用卡提及更明确，作为主意图"
}
```

### Uncertain Intent（模糊意图）
```json
{
  "intent": "uncertain",
  "confidence": 0.3,
  "keywords": ["贷款"],
  "suggestions": [
    {
      "intent": "retail_loan_card",
      "reason": "贷款相关，可能指向零售贷款业务"
    },
    {
      "intent": "credit_knowledge",
      "reason": "贷款关键词，可能查询信贷知识"
    }
  ],
  "need_more_info": true,
  "recommended_questions": [
    "请明确是零售贷款业务还是信贷知识查询？",
    "是否涉及具体的贷款产品（如房贷、车贷）？"
  ]
}
```

### Unknown Intent（无法识别）
```json
{
  "intent": "unknown",
  "confidence": 0,
  "keywords": [],
  "reason": "文本未包含任何预定义意图的关键词或场景信息",
  "matched_category": "无匹配",
  "suggestion": "请提供更多业务背景或明确诉求"
}
```

## Examples

**Example 1: 精确匹配**
```
Input: "我要投诉信用卡盗刷问题"
Output: {
  "intent": "consumer_protection",
  "intent_name": "消保坐席",
  "confidence": 0.92,
  "keywords": ["投诉", "信用卡", "盗刷"],
  "matched_category": "精确匹配",
  "reasoning": "明确的投诉诉求，涉及信用卡业务"
}
```

**Example 2: 关键词匹配**
```
Input: "查询上个月的账户流水明细"
Output: {
  "intent": "transaction_analysis",
  "intent_name": "流水分析",
  "confidence": 0.88,
  "keywords": ["流水", "明细", "账户"],
  "matched_category": "关键词匹配"
}
```

**Example 3: 多意图**
```
Input: "我想申请信用卡，并了解信贷政策"
Output: {
  "intents": [
    {
      "intent": "retail_loan_card",
      "confidence": 0.82,
      "keywords": ["信用卡", "申请"]
    },
    {
      "intent": "credit_knowledge",
      "confidence": 0.75,
      "keywords": ["信贷政策"]
    }
  ],
  "primary_intent": "retail_loan_card",
  "reasoning": "信用卡申请更明确为行动意图，信贷政策查询为辅助意图"
}
```

**Example 4: 模糊意图**
```
Input: "贷款利率怎么样"
Output: {
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

## Handling Edge Cases

### Ambiguous Cases
当文本可能匹配多个意图且置信度相近时：
1. 返回所有可能的意图及置信度
2. 标注 `primary_intent` 作为推荐主意图
3. 提供 `reasoning` 解释为什么选择主意图
4. 如果用户需要精确分类，询问补充信息

### No Match Cases
当文本完全无法匹配预定义意图时：
1. 返回 `intent: unknown`
2. 分析文本特征，提出可能的意图建议
3. 如果可能是新意图类别，建议用户扩展意图体系

### Multi-turn Context
如果用户提供多轮对话上下文：
1. 综合分析所有轮次的关键信息
2. 识别意图演变轨迹（如从咨询→办理）
3. 返回最终意图或意图序列

## Success Metrics

意图识别质量标准：
- **准确率**：对明确意图文本的分类准确率 ≥85%
- **覆盖率**：能识别预定义意图类别中至少 80% 的常见表达
- **响应速度**：单次识别响应时间 <2秒
- **解释性**：每次识别都提供 keywords 和 matched_category 作为证据

## Workflow

1. **接收文本** - 用户输入待识别文本
2. **关键词提取** - 识别业务关键词和场景词
3. **意图匹配** - 匹配到预定义意图类别
4. **置信度计算** - 根据匹配精度计算置信度
5. **结果生成** - 输出结构化 JSON 结果
6. **解释说明** - 提供识别依据和理由

---

**Note:** 此技能专注于银行金融场景的意图识别。如需扩展到其他业务场景，可在 Intent Categories 中添加新的意图类别定义。