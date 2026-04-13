---
name: coding-best-practices
description: Python 编程最佳实践指南，包含代码风格、性能优化、错误处理等建议
---

# Coding Best Practices

## 代码风格

### 基本规则
- 使用 4 个空格缩进（不要用 Tab）
- 行长度不超过 79 字符
- 函数和变量使用 snake_case
- 类名使用 PascalCase
- 常量使用 UPPER_CASE

### 示例
```python
# Good
def calculate_total_price(items):
    total = sum(item.price for item in items)
    return total

# Bad
def calculateTotalPrice(Items):  # 应该用 snake_case
    Total = sum(Item.Price for Item in Items)  # 混乱的命名
    return Total
```

## 性能优化

### 避免在循环中创建对象
```python
# Bad
result = []
for i in range(1000):
    result.append(SomeObject())  # 每次创建新对象

# Good
result = [SomeObject() for i in range(1000)]  # 列表推导式更快
```

### 使用生成器节省内存
```python
# Bad - 占用大量内存
def read_large_file(file_path):
    lines = []
    with open(file_path) as f:
        for line in f:
            lines.append(line)
    return lines

# Good - 使用生成器
def read_large_file(file_path):
    with open(file_path) as f:
        for line in f:
            yield line  # 逐行生成，不占用内存
```

## 错误处理

### 具体的异常类型
```python
# Bad
try:
    process_data(data)
except Exception:  # 太宽泛
    pass

# Good
try:
    process_data(data)
except ValueError as e:
    logger.error(f"数据格式错误: {e}")
except FileNotFoundError:
    logger.error("文件不存在")
```

### 提供有用的错误信息
```python
# Bad
raise ValueError("错误")  # 信息不够

# Good
raise ValueError(f"年龄必须大于 0，当前值: {age}")  # 清晰的错误信息
```

## 文档字符串

### 使用清晰的文档
```python
def calculate_discount(price, discount_rate):
    """
    计算折扣后的价格
    
    Args:
        price: 原价（必须大于 0）
        discount_rate: 折扣率（0-1 之间）
    
    Returns:
        折扣后的价格
    
    Raises:
        ValueError: 如果 price <= 0 或 discount_rate 不在 0-1 范围
    """
    if price <= 0:
        raise ValueError(f"price 必须大于 0，当前: {price}")
    if not (0 <= discount_rate <= 1):
        raise ValueError(f"discount_rate 必须在 0-1 之间，当前: {discount_rate}")
    
    return price * (1 - discount_rate)
```

---

**关键原则：代码应该清晰、可读、可维护。优先考虑可读性而非性能。**