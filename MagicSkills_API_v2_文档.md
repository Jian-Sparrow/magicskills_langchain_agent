# MagicSkills HTTP API v2.0 完整文档

> 基于官方 Python API 实现  
> 文档：https://github.com/Narwhal-Lab/MagicSkills/blob/main/doc/python-api.zh-CN.md

---

## 服务信息

**服务地址**: `http://0.0.0.0:5000`  
**本地访问**: `http://localhost:5000`  
**API 版本**: v2.0

---

## 快速开始

### 启动服务

```bash
cd /home/admin/.openclaw/workspace
sudo /root/miniforge3/envs/magicskills/bin/python magicskills_api_v2.py
```

### 后台运行

```bash
nohup sudo /root/miniforge3/envs/magicskills/bin/python magicskills_api_v2.py > /tmp/magicskills_api.log 2>&1 &

# 查看日志
tail -f /tmp/magicskills_api.log

# 停止服务
pkill -f "python magicskills_api_v2"
```

### 测试连接

```bash
curl http://localhost:5000/health
```

---

## API 端点完整列表

### 📊 基础信息

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | API 首页 |
| `/health` | GET | 健康检查 |

### 🔍 Skills 查询

| 端点 | 方法 | 说明 |
|------|------|------|
| `/skills` | GET | 列出所有可用 skills |
| `/skills/<name>` | GET | 获取单个 skill 详情 |
| `/skills/<name>/content` | GET | 读取 skill 文档内容 |
| `/skills/search` | POST | 搜索 skills |
| `/skills/execute` | POST | 执行 skill 命令 |

### 📦 集合管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/collections` | GET | 列出所有技能集合 |
| `/collections/<name>` | GET | 获取集合详情 |
| `/collections/create` | POST | 创建技能集合 |
| `/collections/<name>/sync` | POST | 同步集合到 AGENTS.md |
| `/collections/<name>` | DELETE | 删除集合 |
| `/collections/<name>/description` | PUT | 更新集合描述 |

### 🛠️ Skill 管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/skills/install` | POST | 安装 skill |
| `/skills/add` | POST | 添加 skill 到集合 |
| `/skills/<name>` | DELETE | 删除 skill |
| `/skills/template` | POST | 创建 skill 模板 |
| `/skills/<name>/upload` | POST | 上传 skill 到仓库 |

### 💾 注册表管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/registry/save` | POST | 保存注册表到磁盘 |
| `/registry/load` | POST | 从磁盘加载注册表 |

### 🔧 统一接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/skill-tool` | POST | 统一的 skill-tool 接口 |

---

## 详细 API 文档

### 基础信息

#### GET `/`

API 首页，返回所有端点列表。

**响应示例:**
```json
{
  "service": "MagicSkills HTTP API",
  "version": "2.0",
  "endpoints": { ... }
}
```

#### GET `/health`

健康检查。

**响应示例:**
```json
{
  "status": "ok",
  "skills_count": 19,
  "collections_count": 2
}
```

---

### Skills 查询

#### GET `/skills`

列出所有可用 skills (Allskills 视图)。

**Query Params:**
- `format`: `json` | `text` (默认：json)

**响应示例:**
```json
{
  "success": true,
  "count": 19,
  "skills": [
    {
      "name": "pdf",
      "description": "Use this skill whenever the user wants to do anything with PDF files...",
      "path": "/home/admin/.openclaw/workspace/skills/allskills/pdf",
      "baseDir": "/home/admin/.openclaw/workspace/skills/allskills",
      "source": "/home/admin/.openclaw/workspace/skills/allskills/pdf",
      "global": false,
      "universal": false
    }
  ]
}
```

#### GET `/skills/<skill_name>`

获取单个 skill 详情。

**Path Params:**
- `skill_name`: skill 名称

**响应示例:**
```json
{
  "success": true,
  "skill": "pdf",
  "content": "=== Skill: pdf ===\nDescription: ...\nPath: ..."
}
```

#### GET `/skills/<skill_name>/content`

读取 skill 文档内容 (SKILL.md)。

**响应示例:**
```json
{
  "success": true,
  "skill": "pdf",
  "content": "---\nname: pdf\ndescription: ...\n---\n\n# PDF Processing Guide\n..."
}
```

#### POST `/skills/search`

搜索 skills。

**Body:**
```json
{
  "query": "pdf",
  "search_in": ["name", "description"]
}
```

**响应示例:**
```json
{
  "success": true,
  "query": "pdf",
  "count": 2,
  "skills": [ ... ]
}
```

#### POST `/skills/execute`

执行 skill 命令。

**Body:**
```json
{
  "command": "python script.py",
  "shell": true,
  "timeout": 60,
  "stream": false
}
```

**响应示例:**
```json
{
  "success": true,
  "command": "python script.py",
  "returncode": 0,
  "stdout": "...",
  "stderr": ""
}
```

---

### 集合管理

#### GET `/collections`

列出所有技能集合。

**响应示例:**
```json
{
  "success": true,
  "count": 2,
  "collections": [
    {
      "name": "office_skills",
      "skills_count": 3,
      "agent_md_path": "/home/admin/.openclaw/workspace/AGENTS.md"
    }
  ]
}
```

#### GET `/collections/<name>`

获取集合详情。

**响应示例:**
```json
{
  "success": true,
  "collection": {
    "name": "office_skills",
    "count": 3,
    "skills": [ ... ],
    "tool_description": "...",
    "cli_description": "...",
    "agent_md_path": "..."
  }
}
```

#### POST `/collections/create`

创建技能集合。

**Body:**
```json
{
  "name": "my_collection",
  "skills": ["pdf", "xlsx", "docx"],
  "paths": ["./skills"],
  "tool_description": "办公技能集合",
  "cli_description": "用于办公自动化任务",
  "agent_md_path": "/path/to/AGENTS.md"
}
```

**响应示例:**
```json
{
  "success": true,
  "message": "集合 'my_collection' 创建成功",
  "collection": { ... }
}
```

#### POST `/collections/<name>/sync`

同步集合到 AGENTS.md。

**Path Params:**
- `name`: 集合名称

**Body:**
```json
{
  "mode": "none",
  "output_path": "/path/to/AGENTS.md"
}
```

**mode 说明:**
- `none`: 保留标准结构
- `cli_description`: 只写 CLI 描述

**响应示例:**
```json
{
  "success": true,
  "message": "集合 'my_collection' 同步成功",
  "output_path": "/home/admin/.openclaw/workspace/AGENTS.md"
}
```

#### DELETE `/collections/<name>`

删除集合。

**响应示例:**
```json
{
  "success": true,
  "message": "集合 'my_collection' 已删除"
}
```

#### PUT `/collections/<name>/description`

更新集合描述。

**Body:**
```json
{
  "tool_description": "新的工具描述",
  "cli_description": "新的 CLI 描述"
}
```

---

### Skill 管理

#### POST `/skills/install`

安装 skill。

**Body:**
```json
{
  "source": "本地路径 / GitHub 仓库 / skill 名称",
  "global": false,
  "universal": false,
  "yes": true,
  "target_root": "/custom/path"
}
```

**响应示例:**
```json
{
  "success": true,
  "message": "安装了 1 个 skills",
  "paths": ["/home/admin/.../skills/pdf"]
}
```

#### POST `/skills/add`

添加 skill 到集合。

**Body:**
```json
{
  "collection": "office_skills",
  "target": "pdf"
}
```

#### DELETE `/skills/<skill_name>`

删除 skill。

**响应示例:**
```json
{
  "success": true,
  "message": "Skill 'pdf' 已删除",
  "deleted_path": "/home/admin/.../skills/pdf"
}
```

#### POST `/skills/template`

创建 skill 模板。

**Body:**
```json
{
  "name": "my_new_skill",
  "base_dir": "/home/admin/.openclaw/workspace/skills/allskills"
}
```

**响应示例:**
```json
{
  "success": true,
  "message": "Skill 模板已创建",
  "path": "/home/admin/.../skills/my_new_skill"
}
```

#### POST `/skills/<skill_name>/upload`

上传 skill 到仓库。

**响应示例:**
```json
{
  "success": true,
  "skill_name": "pdf",
  "repo": "https://github.com/...",
  "branch": "main",
  "committed": true,
  "pushed": true,
  "pr_url": "https://github.com/.../pull/1"
}
```

---

### 注册表管理

#### POST `/registry/save`

保存注册表到磁盘。

**响应示例:**
```json
{
  "success": true,
  "message": "注册表已保存",
  "path": "/path/to/registry.json"
}
```

#### POST `/registry/load`

从磁盘加载注册表。

**响应示例:**
```json
{
  "success": true,
  "message": "注册表已加载",
  "collections_count": 2
}
```

---

### 统一接口

#### POST `/skill-tool`

统一的 skill-tool 接口（兼容 CLI）。

**Body:**
```json
{
  "action": "listskill",
  "arg": "",
  "name": "office_skills"
}
```

**支持的 action:**
- `listskill`: 列出 skills
- `readskill`: 读取 skill 文档
- `execskill`: 执行命令

**响应示例:**
```json
{
  "success": true,
  "action": "listskill",
  "result": "1. name: pdf\n   description: ..."
}
```

---

## 使用示例

### 示例 1: Python 调用

```python
import requests

API_BASE = "http://localhost:5000"

# 列出所有 skills
resp = requests.get(f"{API_BASE}/skills")
skills = resp.json()['skills']
print(f"找到 {len(skills)} 个 skills")

# 读取 skill 文档
resp = requests.get(f"{API_BASE}/skills/pdf/content")
doc = resp.json()['content']
print(doc[:200])

# 搜索 skills
resp = requests.post(f"{API_BASE}/skills/search", 
                    json={"query": "pdf"})
matched = resp.json()['skills']
print(f"找到 {len(matched)} 个 PDF 相关技能")

# 创建集合
resp = requests.post(f"{API_BASE}/collections/create",
                    json={
                        "name": "office_skills",
                        "skills": ["pdf", "xlsx", "docx"]
                    })
print(resp.json())

# 同步集合
resp = requests.post(f"{API_BASE}/collections/office_skills/sync",
                    json={"mode": "none"})
print(resp.json())
```

### 示例 2: cURL 命令

```bash
# 列出所有 skills
curl http://localhost:5000/skills

# 读取 skill 文档
curl http://localhost:5000/skills/pdf/content

# 搜索 skills
curl -X POST http://localhost:5000/skills/search \
  -H "Content-Type: application/json" \
  -d '{"query": "pdf"}'

# 创建集合
curl -X POST http://localhost:5000/collections/create \
  -H "Content-Type: application/json" \
  -d '{"name":"office_skills","skills":["pdf","xlsx","docx"]}'

# 同步集合
curl -X POST http://localhost:5000/collections/office_skills/sync \
  -H "Content-Type: application/json" \
  -d '{"mode":"none"}'

# 执行命令
curl -X POST http://localhost:5000/skills/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"echo hello","shell":true}'
```

### 示例 3: Node.js 调用

```javascript
const axios = require('axios');

const API_BASE = 'http://localhost:5000';

async function listSkills() {
    const resp = await axios.get(`${API_BASE}/skills`);
    return resp.data.skills;
}

async function readSkill(skillName) {
    const resp = await axios.get(`${API_BASE}/skills/${skillName}/content`);
    return resp.data.content;
}

async function createCollection(name, skills) {
    const resp = await axios.post(`${API_BASE}/collections/create`, {
        name,
        skills
    });
    return resp.data;
}

// 使用示例
(async () => {
    const skills = await listSkills();
    console.log(`找到 ${skills.length} 个 skills`);
    
    const pdfDoc = await readSkill('pdf');
    console.log(pdfDoc.substring(0, 200));
    
    const result = await createCollection('office_skills', ['pdf', 'xlsx']);
    console.log(result);
})();
```

### 示例 4: LangChain 集成

```python
from langchain.tools import tool
import requests

API_BASE = "http://localhost:5000"

@tool
def list_magic_skills() -> str:
    """列出所有可用的 MagicSkills"""
    resp = requests.get(f"{API_BASE}/skills")
    data = resp.json()
    return f"找到 {data['count']} 个 skills:\n" + "\n".join([
        f"- {s['name']}: {s['description'][:100]}..."
        for s in data['skills']
    ])

@tool
def read_skill_doc(skill_name: str) -> str:
    """读取指定 skill 的文档"""
    resp = requests.get(f"{API_BASE}/skills/{skill_name}/content")
    return resp.json()['content']

@tool
def search_skills(query: str) -> str:
    """搜索 skills"""
    resp = requests.get(f"{API_BASE}/skills/search", 
                       params={"query": query})
    data = resp.json()
    return f"找到 {data['count']} 个匹配"

# 在 Agent 中使用
from langchain.agents import initialize_agent, Tool

tools = [
    Tool(name="ListMagicSkills", func=list_magic_skills),
    Tool(name="ReadSkillDoc", func=read_skill_doc),
    Tool(name="SearchSkills", func=search_skills),
]

agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
agent.run("有哪些处理 PDF 的 skills？")
```

---

## 错误处理

所有 API 返回统一的 JSON 格式：

**成功:**
```json
{
  "success": true,
  "data": { ... }
}
```

**失败:**
```json
{
  "success": false,
  "error": "错误信息"
}
```

**HTTP 状态码:**
- `200` - 成功
- `400` - 请求参数错误
- `404` - 资源不存在
- `500` - 服务器错误

---

## 与 v1 的区别

| 特性 | v1 (CLI 封装) | v2 (官方 API) |
|------|-------------|-------------|
| 实现方式 | 调用 CLI 命令 | 直接调用 Python API |
| 性能 | 较慢 (子进程) | 快 (直接调用) |
| 错误处理 | 解析 stdout | 异常捕获 |
| 功能完整性 | 部分 | 完整 |
| 推荐度 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 故障排查

### 服务无法启动

```bash
# 检查端口
netstat -tlnp | grep 5000

# 查看日志
tail -f /tmp/magicskills_api.log
```

### 找不到 magicskills 模块

```bash
# 确认环境
sudo /root/miniforge3/envs/magicskills/bin/python -c "import magicskills; print('OK')"
```

### API 返回错误

```bash
# 测试健康检查
curl http://localhost:5000/health

# 检查 skills 目录
ls /home/admin/.openclaw/workspace/skills/allskills/*/SKILL.md
```

---

**文档版本**: v2.0  
**更新时间**: 2026-03-30  
**官方文档**: https://github.com/Narwhal-Lab/MagicSkills/blob/main/doc/python-api.zh-CN.md
