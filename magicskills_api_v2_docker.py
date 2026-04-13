#!/usr/bin/env python3
"""
MagicSkills HTTP API Server (Docker版本)
基于官方Python API，参数化配置用于容器化部署

文档：https://github.com/Narwhal-Lab/MagicSkills/blob/main/doc/python-api.zh-CN.md
"""

import os
from pathlib import Path
from flask import Flask, request, jsonify
import json

# magicskills通过pip安装，无需手动添加sys.path
from magicskills import (
    ALL_SKILLS,
    REGISTRY,
    Skills,
    listskill,
    readskill,
    showskill,
    execskill,
    addskill,
    createskill_template,
    install,
    uploadskill,
    deleteskill,
    addskills,
    listskills,
    deleteskills,
    syncskills,
    loadskills,
    saveskills,
    change_tool_description,
    change_cli_description,
    skill_tool,
)

app = Flask(__name__)

# 配置 - 从环境变量读取
SKILLS_DIR = Path(os.getenv("SKILLS_DIR", "/app/workspace/skills/allskills"))
AGENTS_MD_PATH = Path(os.getenv("AGENTS_MD_PATH", "/app/workspace/AGENTS.md"))

# 确保目录存在
SKILLS_DIR.mkdir(parents=True, exist_ok=True)
if not AGENTS_MD_PATH.exists():
    AGENTS_MD_PATH.touch()

# 初始化Allskills集合（使用环境变量配置的路径）
def init_all_skills():
    """初始化Allskills集合并注册到全局REGISTRY"""
    try:
        # 创建Skills对象，扫描SKILLS_DIR目录
        all_skills = Skills(
            name="Allskills",
            paths=[str(SKILLS_DIR)],
            agent_md_path=str(AGENTS_MD_PATH)
        )
        # 注册到全局REGISTRY
        REGISTRY.register(all_skills)
        print(f"✅ Initialized Allskills with {len(all_skills.skills)} skills")
        return all_skills
    except Exception as e:
        print(f"❌ Failed to initialize Allskills: {e}")
        return None

# 初始化Allskills
_ALL_SKILLS_INSTANCE = init_all_skills()

# 覆盖ALL_SKILLS函数以使用我们的实例
def ALL_SKILLS():
    """返回初始化的Allskills实例"""
    return _ALL_SKILLS_INSTANCE or Skills(name="Allskills", paths=[str(SKILLS_DIR)])


# ==================== 辅助函数 ====================

def skill_to_dict(skill):
    """将 Skill 对象转换为字典"""
    if hasattr(skill, 'to_dict'):
        return skill.to_dict()
    return {
        "name": skill.name,
        "description": skill.description,
        "path": str(skill.path),
        "base_dir": str(skill.base_dir),
        "source": skill.source,
        "is_global": skill.is_global,
        "universal": skill.universal,
    }


def skills_list_to_dict(skills_obj):
    """将 Skills 对象转换为字典"""
    return {
        "name": skills_obj.name,
        "count": len(skills_obj.skills),
        "skills": [skill_to_dict(s) for s in skills_obj.skills],
        "tool_description": skills_obj.tool_description,
        "cli_description": skills_obj.cli_description,
        "agent_md_path": str(skills_obj.agent_md_path),
    }


# ==================== 基础信息 ====================

@app.route('/', methods=['GET'])
def index():
    """API 首页"""
    return jsonify({
        "service": "MagicSkills HTTP API",
        "version": "2.0-docker",
        "description": "基于官方 Python API 的 Docker 容器化实现",
        "endpoints": {
            "GET /health": "健康检查",
            "GET /skills": "列出所有可用 skills (Allskills)",
            "GET /skills/<name>": "获取单个 skill 详情",
            "GET /skills/<name>/content": "读取 skill 文档内容",
            "POST /skills/search": "搜索 skills",
            "POST /skills/execute": "执行 skill 命令",
            "GET /collections": "列出所有技能集合",
            "POST /collections/create": "创建技能集合",
            "POST /collections/<name>/sync": "同步集合到 AGENTS.md",
            "DELETE /collections/<name>": "删除集合",
            "POST /skills/install": "安装 skill",
            "POST /skills/add": "添加 skill 到集合",
            "DELETE /skills/<name>": "删除 skill",
            "POST /skills/template": "创建 skill 模板",
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "service": "magicskills-api",
        "skills_count": len(ALL_SKILLS().skills),
        "collections_count": len(listskills()),
    })


# ==================== Skills 查询 ====================

@app.route('/skills', methods=['GET'])
def list_all_skills():
    """
    列出所有可用 skills (Allskills 视图)

    Query Params:
        format: json | text (默认：json)
    """
    fmt = request.args.get('format', 'json')

    try:
        if fmt == 'text':
            result = listskill(ALL_SKILLS())
            return jsonify({
                "success": True,
                "format": "text",
                "content": result
            })
        else:
            skills = ALL_SKILLS()
            return jsonify({
                "success": True,
                "count": len(skills.skills),
                "skills": [skill_to_dict(s) for s in skills.skills]
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/skills/<skill_name>', methods=['GET'])
def get_skill(skill_name):
    """
    获取单个 skill 详情

    Path Params:
        skill_name: skill 名称
    """
    try:
        result = showskill(ALL_SKILLS(), skill_name)
        return jsonify({
            "success": True,
            "skill": skill_name,
            "content": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404


@app.route('/skills/<skill_name>/content', methods=['GET'])
def get_skill_content(skill_name):
    """
    读取 skill 文档内容 (SKILL.md)

    Path Params:
        skill_name: skill 名称
    """
    try:
        content = readskill(ALL_SKILLS(), skill_name)
        return jsonify({
            "success": True,
            "skill": skill_name,
            "content": content
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404


@app.route('/skills/search', methods=['POST'])
def search_skills():
    """
    搜索 skills

    Body:
        {
            "query": "搜索关键词",
            "search_in": ["name", "description"]  // 可选
        }
    """
    data = request.json
    if not data or 'query' not in data:
        return jsonify({
            "success": False,
            "error": "需要提供 query 参数"
        }), 400

    query = data['query'].lower()
    search_in = data.get('search_in', ['name', 'description'])

    try:
        skills = ALL_SKILLS()
        matched = []

        for skill in skills.skills:
            match = False
            if 'name' in search_in and query in skill.name.lower():
                match = True
            if 'description' in search_in and query in skill.description.lower():
                match = True

            if match:
                matched.append(skill_to_dict(skill))

        return jsonify({
            "success": True,
            "query": query,
            "count": len(matched),
            "skills": matched
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/skills/execute', methods=['POST'])
def execute_skill():
    """
    执行 skill 命令

    Body:
        {
            "command": "要执行的命令",
            "shell": true,  // 可选，默认 true
            "timeout": 60,  // 可选，超时时间（秒）
            "stream": false  // 可选，是否流式输出
        }
    """
    data = request.json
    if not data or 'command' not in data:
        return jsonify({
            "success": False,
            "error": "需要提供 command 参数"
        }), 400

    command = data['command']
    shell = data.get('shell', True)
    timeout = data.get('timeout')
    stream = data.get('stream', False)

    try:
        result = execskill(
            ALL_SKILLS(),
            command,
            shell=shell,
            timeout=timeout,
            stream=stream
        )

        return jsonify({
            "success": result.returncode == 0,
            "command": result.command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== 集合管理 ====================

@app.route('/collections', methods=['GET'])
def list_collections():
    """列出所有技能集合"""
    try:
        collections = listskills()
        return jsonify({
            "success": True,
            "count": len(collections),
            "collections": [
                {
                    "name": c.name,
                    "skills_count": len(c.skills),
                    "agent_md_path": str(c.agent_md_path),
                }
                for c in collections
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/collections/<name>', methods=['GET'])
def get_collection(name):
    """获取集合详情"""
    try:
        collection = REGISTRY.get_skills(name)
        return jsonify({
            "success": True,
            "collection": skills_list_to_dict(collection)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404


@app.route('/collections/create', methods=['POST'])
def create_collection():
    """
    创建技能集合

    Body:
        {
            "name": "集合名称",
            "skills": ["skill1", "skill2"],  // 可选，skill 名称列表
            "paths": ["./skills"],  // 可选，skills 目录列表
            "tool_description": "...",  // 可选
            "cli_description": "...",  // 可选
            "agent_md_path": "..."  // 可选
        }
    """
    data = request.json
    if not data or 'name' not in data:
        return jsonify({
            "success": False,
            "error": "需要提供 name 参数"
        }), 400

    try:
        skills_obj = addskills(
            name=data['name'],
            skill_list=data.get('skills'),
            paths=data.get('paths'),
            tool_description=data.get('tool_description'),
            cli_description=data.get('cli_description'),
            agent_md_path=data.get('agent_md_path', str(AGENTS_MD_PATH))
        )

        saveskills()  # 持久化

        return jsonify({
            "success": True,
            "message": f"集合 '{data['name']}' 创建成功",
            "collection": skills_list_to_dict(skills_obj)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/collections/<name>/sync', methods=['POST'])
def sync_collection(name):
    """
    同步集合到 AGENTS.md

    Path Params:
        name: 集合名称

    Body:
        {
            "mode": "none",  // none | cli_description
            "output_path": "..."  // 可选，覆盖默认路径
        }
    """
    data = request.json or {}

    try:
        collection = REGISTRY.get_skills(name)
        output_path = data.get('output_path')
        mode = data.get('mode', 'none')

        path = syncskills(collection, output_path=output_path, mode=mode)

        return jsonify({
            "success": True,
            "message": f"集合 '{name}' 同步成功",
            "output_path": str(path)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/collections/<name>', methods=['DELETE'])
def delete_collection(name):
    """删除集合"""
    try:
        deleteskills(name)
        return jsonify({
            "success": True,
            "message": f"集合 '{name}' 已删除"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== Skill 管理 ====================

@app.route('/skills/install', methods=['POST'])
def install_skill():
    """
    安装 skill

    Body:
        {
            "source": "本地路径 / GitHub 仓库 / skill 名称",
            "global": false,  // 可选
            "universal": false,  // 可选
            "yes": true,  // 可选，覆盖已存在的
            "target_root": "..."  // 可选，自定义安装目录
        }
    """
    data = request.json
    if not data or 'source' not in data:
        return jsonify({
            "success": False,
            "error": "需要提供 source 参数"
        }), 400

    try:
        paths = install(
            source=data['source'],
            global_=data.get('global', False),
            universal=data.get('universal', False),
            yes=data.get('yes', False),
            target_root=data.get('target_root')
        )

        return jsonify({
            "success": True,
            "message": f"安装了 {len(paths)} 个 skills",
            "paths": [str(p) for p in paths]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/skills/add', methods=['POST'])
def add_skill_to_collection():
    """
    添加 skill 到集合

    Body:
        {
            "collection": "集合名称",  // 可选，默认添加到 Allskills
            "target": "skill 名称或路径"
        }
    """
    data = request.json
    if not data or 'target' not in data:
        return jsonify({
            "success": False,
            "error": "需要提供 target 参数"
        }), 400

    try:
        collection_name = data.get('collection', 'Allskills')
        if collection_name == 'Allskills':
            skills_obj = ALL_SKILLS()
        else:
            skills_obj = REGISTRY.get_skills(collection_name)

        path = addskill(skills_obj, data['target'])

        return jsonify({
            "success": True,
            "message": f"Skill 已添加",
            "path": str(path)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/skills/<skill_name>', methods=['DELETE'])
def delete_skill(skill_name):
    """删除 skill"""
    try:
        deleted = deleteskill(ALL_SKILLS(), skill_name)
        return jsonify({
            "success": True,
            "message": f"Skill '{skill_name}' 已删除",
            "deleted_path": deleted
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/skills/template', methods=['POST'])
def create_skill_template():
    """
    创建 skill 模板

    Body:
        {
            "name": "skill 名称",
            "base_dir": "..."  // 可选，默认 SKILLS_DIR
        }
    """
    data = request.json
    if not data or 'name' not in data:
        return jsonify({
            "success": False,
            "error": "需要提供 name 参数"
        }), 400

    try:
        base_dir = data.get('base_dir', str(SKILLS_DIR))
        path = createskill_template(data['name'], base_dir)

        return jsonify({
            "success": True,
            "message": f"Skill 模板已创建",
            "path": str(path)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/skills/<skill_name>/upload', methods=['POST'])
def upload_skill(skill_name):
    """
    上传 skill 到仓库

    Path Params:
        skill_name: skill 名称
    """
    try:
        result = uploadskill(ALL_SKILLS(), skill_name)
        return jsonify({
            "success": True,
            "skill_name": result.skill_name,
            "repo": result.repo,
            "branch": result.branch,
            "committed": result.committed,
            "pushed": result.pushed,
            "pr_url": result.pr_url if hasattr(result, 'pr_url') else None
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== 注册表管理 ====================

@app.route('/registry/save', methods=['POST'])
def save_registry():
    """保存注册表到磁盘"""
    try:
        path = saveskills()
        return jsonify({
            "success": True,
            "message": "注册表已保存",
            "path": path
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/registry/load', methods=['POST'])
def load_registry():
    """从磁盘加载注册表"""
    try:
        collections = loadskills()
        return jsonify({
            "success": True,
            "message": "注册表已加载",
            "collections_count": len(collections)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/collections/<name>/description', methods=['PUT'])
def update_collection_description(name):
    """
    更新集合描述

    Path Params:
        name: 集合名称

    Body:
        {
            "tool_description": "...",  // 可选
            "cli_description": "..."  // 可选
        }
    """
    data = request.json
    if not data:
        return jsonify({
            "success": False,
            "error": "需要提供描述信息"
        }), 400

    try:
        collection = REGISTRY.get_skills(name)

        if 'tool_description' in data:
            change_tool_description(collection, data['tool_description'])

        if 'cli_description' in data:
            change_cli_description(collection, data['cli_description'])

        saveskills()  # 持久化

        return jsonify({
            "success": True,
            "message": f"集合 '{name}' 描述已更新"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== Skill Tool 统一接口 ====================

@app.route('/skill-tool', methods=['POST'])
def skill_tool_api():
    """
    统一的 skill-tool 接口（兼容 CLI）

    Body:
        {
            "action": "listskill | readskill | execskill",
            "arg": "参数",
            "name": "集合名称"  // 可选
        }
    """
    data = request.json
    if not data or 'action' not in data:
        return jsonify({
            "success": False,
            "error": "需要提供 action 参数"
        }), 400

    action = data['action']
    arg = data.get('arg', '')
    name = data.get('name', 'Allskills')

    try:
        if name == 'Allskills':
            skills_obj = ALL_SKILLS()
        else:
            skills_obj = REGISTRY.get_skills(name)

        result = skill_tool(skills_obj, action, arg)

        return jsonify({
            "success": True,
            "action": action,
            "result": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("MagicSkills HTTP API Server v2.0 (Docker)")
    print("=" * 60)
    print(f"基于官方 Python API，参数化配置")
    print(f"Skills Directory: {SKILLS_DIR}")
    print(f"AGENTS.md: {AGENTS_MD_PATH}")
    print("=" * 60)
    print(f"当前 skills 数量：{len(ALL_SKILLS().skills)}")
    print(f"当前集合数量：{len(listskills())}")
    print("=" * 60)
    print("Starting server on http://0.0.0.0:5000")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=False)