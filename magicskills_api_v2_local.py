#!/usr/bin/env python3
"""
MagicSkills HTTP API Server (Local macOS Version)
Modified for local testing on macOS

Changes from original:
- Removed hardcoded Linux paths
- Uses local workspace directory
- Uses port 5001 (5000 used by AirPlay Receiver on macOS)
"""

import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify
import json

# magicskills is now available in venv, no need to add to path

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

# Local macOS configuration
BASE_DIR = Path(__file__).parent
SKILLS_DIR = BASE_DIR / "workspace" / "skills" / "allskills"
AGENTS_MD_PATH = BASE_DIR / "workspace" / "AGENTS.md"

# Ensure directories exist
SKILLS_DIR.mkdir(parents=True, exist_ok=True)
AGENTS_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
if not AGENTS_MD_PATH.exists():
    AGENTS_MD_PATH.touch()


# ==================== Helper Functions ====================

def skill_to_dict(skill):
    """Convert Skill object to dictionary"""
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
    """Convert Skills object to dictionary"""
    return {
        "name": skills_obj.name,
        "count": len(skills_obj.skills),
        "skills": [skill_to_dict(s) for s in skills_obj.skills],
        "tool_description": skills_obj.tool_description,
        "cli_description": skills_obj.cli_description,
        "agent_md_path": str(skills_obj.agent_md_path),
    }


# ==================== Health and Info ====================

@app.route('/', methods=['GET'])
def index():
    """API Home"""
    return jsonify({
        "service": "MagicSkills HTTP API (Local macOS)",
        "version": "2.0-local",
        "description": "Modified for local macOS testing",
        "endpoints": {
            "GET /health": "Health check",
            "GET /skills": "List all skills",
            "GET /skills/<name>": "Get skill details",
            "GET /skills/<name>/content": "Read skill documentation",
            "POST /skills/search": "Search skills",
            "POST /skills/execute": "Execute skill command",
            "GET /collections": "List collections",
            "POST /collections/create": "Create collection",
            "POST /skill-tool": "Unified skill-tool interface (CLI compatible)",
        },
        "config": {
            "skills_dir": str(SKILLS_DIR),
            "agents_md": str(AGENTS_MD_PATH),
            "port": 5001,
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "service": "magicskills-api-local",
        "skills_count": len(ALL_SKILLS().skills),
        "collections_count": len(listskills()),
    })


# ==================== Skills Query ====================

@app.route('/skills', methods=['GET'])
def list_all_skills():
    """List all available skills"""
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
    """Get single skill details"""
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
    """Read skill documentation (SKILL.md)"""
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
    """Search skills"""
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
    """Execute skill command"""
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


# ==================== Collections ====================

@app.route('/collections', methods=['GET'])
def list_collections():
    """List all collections"""
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
    """Get collection details"""
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
    """Create collection"""
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

        saveskills()

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


# ==================== Skill Tool Interface ====================

@app.route('/skill-tool', methods=['POST'])
def skill_tool_api():
    """
    Unified skill-tool interface (CLI compatible)

    Body:
        {
            "action": "listskill | readskill | execskill",
            "arg": "参数",
            "name": "集合名称"  // optional
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
    print("="*60)
    print("MagicSkills HTTP API Server (Local macOS)")
    print("="*60)
    print(f"Based on official Python API")
    print(f"Skills Directory: {SKILLS_DIR}")
    print(f"AGENTS.md: {AGENTS_MD_PATH}")
    print("="*60)
    print(f"Current skills count: {len(ALL_SKILLS().skills)}")
    print(f"Current collections count: {len(listskills())}")
    print("="*60)
    print("Starting server on http://localhost:5001")
    print("="*60)

    app.run(host='localhost', port=5001, debug=False)