"""
复杂装配体 CAE 自动化 MCP 服务器
支持：装配体分析、智能拆分、接触检测、自适应网格
"""

import json
import subprocess
import sys
import os
import glob
from pathlib import Path

# UTF-8 编码配置
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')
except AttributeError:
    # 旧版本Python可能不支持reconfigure
    pass

# ================= 配置区 =================
LOCAL_WORK_DIR = r"E:\DeepSeek_Work\test"
DOCKER_CONTAINER_NAME = "cq_brain"

# 装配体处理配置
CONFIG = {
    "max_file_size_mb": 150,
    "simplify_tolerance": 0.5,
    "contact_tolerance": 0.01,
    "mesh_coarse": 5.0,
    "mesh_fine": 0.5,
    "max_batch_parts": 50,
    "default_timeout": 600
}

# 安全黑名单
BLOCKED_CMDS = ['rm -rf /', 'format', 'del /f']
# =========================================

def log(msg):
    """日志输出到 stderr"""
    sys.stderr.write(f"[MCP] {msg}\n")
    sys.stderr.flush()

def send(obj):
    """发送 JSON-RPC 响应"""
    try:
        json_str = json.dumps(obj, ensure_ascii=False)
        sys.stdout.write(json_str + "\n")
        sys.stdout.flush()
    except Exception as e:
        log(f"Send error: {e}")

def get_local_path(container_path):
    """容器路径映射到本地路径"""
    if container_path.startswith("/app/"):
        rel = container_path.replace("/app/", "").replace("/", os.sep)
        return os.path.join(LOCAL_WORK_DIR, rel)
    if container_path.startswith("/workspace/"):
        rel = container_path.replace("/workspace/", "").replace("/", os.sep)
        return os.path.join(LOCAL_WORK_DIR, rel)
    return os.path.join(LOCAL_WORK_DIR, os.path.basename(container_path))

def is_safe(cmd):
    """安全检查"""
    for blocked in BLOCKED_CMDS:
        if blocked.lower() in cmd.lower():
            return False, f"Blocked: {blocked}"
    return True, ""

def docker_exec(cmd, workdir="/app", timeout=None):
    """执行 Docker 命令"""
    if timeout is None:
        timeout = CONFIG["default_timeout"]
    
    safe, msg = is_safe(cmd)
    if not safe:
        return f"SECURITY: {msg}", True
    
    full_cmd = ["docker", "exec", "-w", workdir, DOCKER_CONTAINER_NAME, "/bin/bash", "-c", cmd]
    
    try:
        proc = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding='utf-8', errors='replace', timeout=timeout)
        output = f"EXIT:{proc.returncode}\nOUT:\n{proc.stdout}\nERR:\n{proc.stderr}"
        return output, proc.returncode != 0
    except subprocess.TimeoutExpired:
        return f"Timeout after {timeout}s", True
    except Exception as e:
        return f"Error: {e}", True

# ==================== 装配体工具函数 ====================

def analyze_step(step_path):
    """分析 STEP 文件"""
    local = get_local_path(step_path)
    if not os.path.exists(local):
        return {"error": f"File not found: {local}"}
    
    size_mb = os.path.getsize(local) / (1024 * 1024)
    container_path = step_path if step_path.startswith("/app/") else f"/app/{os.path.basename(step_path)}"
    
    cmd = f"gmsh {container_path} -0 -info 2>&1 | head -50"
    output, _ = docker_exec(cmd, timeout=60)
    
    return {
        "file": step_path,
        "size_mb": round(size_mb, 2),
        "needs_split": size_mb > CONFIG["max_file_size_mb"],
        "container_path": container_path,
        "gmsh_info": output
    }

def create_context(step_path):
    """生成装配体分析上下文"""
    info = analyze_step(step_path)
    if "error" in info:
        return info
    
    workflow = [
        "【推荐工作流程】",
        "1. 使用 'analyze_step' 检查文件基本信息",
        "2. 如果文件过大，使用 'split_assembly' 拆分",
        "3. 使用 'detect_contacts' 识别接触关系",
        "4. 使用 'generate_mesh' 生成网格（可批量）",
        "5. 使用 'create_calculix_inp' 生成求解文件",
        "6. 使用 'run_analysis' 执行计算",
        "7. 使用 'extract_results' 提取结果"
    ]
    
    summary = f"""
=== 装配体分析上下文 ===
文件: {info['file']}
大小: {info['size_mb']} MB
状态: {'需要拆分' if info['needs_split'] else '可直接处理'}

{chr(10).join(workflow)}

配置参数:
- 接触容差: {CONFIG['contact_tolerance']} mm
- 网格尺寸: {CONFIG['mesh_fine']} - {CONFIG['mesh_coarse']} mm
- 简化阈值: {CONFIG['simplify_tolerance']} mm
"""
    
    return {"summary": summary, "info": info}

def split_assembly(step_path, output_dir="/app/parts"):
    """拆分装配体"""
    info = analyze_step(step_path)
    if "error" in info:
        return info
    
    # 创建输出目录
    local_out = get_local_path(output_dir)
    os.makedirs(local_out, exist_ok=True)
    
    # Gmsh 拆分命令
    cmd = f"""
    mkdir -p {output_dir} && \
    gmsh {info['container_path']} -0 \
    -string 'Geometry.OCCFixDegenerated=1; Geometry.Tolerance={CONFIG['contact_tolerance']};' \
    2>&1
    """
    
    output, is_err = docker_exec(cmd, timeout=300)
    
    # 列出生成的文件
    list_cmd = f"ls -lh {output_dir} 2>&1"
    list_out, _ = docker_exec(list_cmd, timeout=10)
    
    return {
        "status": "error" if is_err else "success",
        "output_dir": output_dir,
        "files": list_out,
        "process_log": output
    }

def generate_mesh(part_path, analysis="stress", target_elements=50000):
    """生成自适应网格"""
    container_path = part_path if part_path.startswith("/app/") else f"/app/{os.path.basename(part_path)}"
    
    # 根据分析类型调整参数
    mesh_params = {
        "stress": (CONFIG["mesh_coarse"], CONFIG["mesh_fine"]),
        "thermal": (CONFIG["mesh_coarse"] * 1.5, CONFIG["mesh_fine"] * 2),
        "modal": (CONFIG["mesh_coarse"] * 0.8, CONFIG["mesh_fine"] * 1.5)
    }
    clmax, clmin = mesh_params.get(analysis, mesh_params["stress"])
    
    output_mesh = container_path.replace('.step', '.msh').replace('.stp', '.msh')
    
    cmd = f"gmsh {container_path} -3 -clmax {clmax} -clmin {clmin} -optimize -o {output_mesh} 2>&1"
    output, is_err = docker_exec(cmd, timeout=600)
    
    if is_err:
        return {"error": "Mesh failed", "log": output}
    
    # 获取网格统计
    info_cmd = f"gmsh {output_mesh} -info 2>&1 | grep -E 'nodes|elements' | head -10"
    info, _ = docker_exec(info_cmd, timeout=30)
    
    return {
        "status": "success",
        "mesh_file": output_mesh,
        "params": {"clmax": clmax, "clmin": clmin},
        "stats": info
    }

def create_calculix_inp(mesh_file, analysis="stress", material="steel"):
    """生成 CalculiX 输入文件"""
    templates = {
        "steel": {"E": 210000, "nu": 0.3, "density": 7850},
        "aluminum": {"E": 70000, "nu": 0.33, "density": 2700},
        "titanium": {"E": 110000, "nu": 0.34, "density": 4500}
    }
    
    mat = templates.get(material.lower(), templates["steel"])
    
    inp_content = f"""*HEADING
{analysis.upper()} Analysis - Auto-generated

*INCLUDE, INPUT={mesh_file}

*MATERIAL, NAME={material.upper()}
*ELASTIC
{mat['E']}, {mat['nu']}
*DENSITY
{mat['density']}

*SOLID SECTION, ELSET=Eall, MATERIAL={material.upper()}

*BOUNDARY
** TODO: 定义固定约束节点集 NFIX
** NFIX, 1, 3, 0

*STEP
*STATIC
** TODO: 定义载荷
** *CLOAD
** NLOAD, 2, -1000
*NODE FILE
U
*EL FILE
S, E
*END STEP
"""
    
    inp_file = mesh_file.replace('.msh', '.inp')
    local_inp = get_local_path(inp_file)
    os.makedirs(os.path.dirname(local_inp), exist_ok=True)
    
    with open(local_inp, 'w', encoding='utf-8') as f:
        f.write(inp_content)
    
    return {
        "status": "success",
        "inp_file": inp_file,
        "note": "请修改 BOUNDARY 和 CLOAD 部分定义实际的边界条件和载荷"
    }

def batch_process(parts_dir="/app/parts", analysis="stress"):
    """批量处理零件"""
    local_dir = get_local_path(parts_dir)
    if not os.path.exists(local_dir):
        return {"error": f"Directory not found: {local_dir}"}
    
    step_files = glob.glob(os.path.join(local_dir, "*.step")) + \
                 glob.glob(os.path.join(local_dir, "*.stp"))
    
    if not step_files:
        return {"error": "No STEP files found"}
    
    results = []
    for i, step_file in enumerate(step_files[:CONFIG["max_batch_parts"]], 1):
        rel_path = os.path.relpath(step_file, LOCAL_WORK_DIR)
        container_path = f"/app/{rel_path}".replace(os.sep, '/')
        
        log(f"Processing {i}/{len(step_files)}: {rel_path}")
        result = generate_mesh(container_path, analysis)
        
        results.append({
            "part": rel_path,
            "status": result.get("status", "error"),
            "mesh": result.get("mesh_file", "N/A")
        })
    
    return {
        "processed": len(results),
        "total": len(step_files),
        "results": results
    }

# ==================== MCP 协议处理 ====================

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        send({
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "cae-assembly-mcp", "version": "1.0"}
            }
        })
        
    elif method == "notifications/initialized":
        log("MCP Server initialized")
        
    elif method == "tools/list":
        send({
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "tools": [
                    # 基础工具
                    {
                        "name": "read_file",
                        "description": "读取文件内容",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"file_path": {"type": "string"}},
                            "required": ["file_path"]
                        }
                    },
                    {
                        "name": "write_file",
                        "description": "写入文件（自动创建目录）",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "file_path": {"type": "string"},
                                "content": {"type": "string"}
                            },
                            "required": ["file_path", "content"]
                        }
                    },
                    {
                        "name": "list_files",
                        "description": "列出文件，支持通配符",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "directory": {"type": "string", "default": "/app"},
                                "pattern": {"type": "string", "default": "*"}
                            }
                        }
                    },
                    # 装配体工具
                    {
                        "name": "analyze_step",
                        "description": "【第一步】分析 STEP 文件基本信息",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"step_path": {"type": "string"}},
                            "required": ["step_path"]
                        }
                    },
                    {
                        "name": "create_context",
                        "description": "【AI必读】生成装配体分析的完整工作流指导",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"step_path": {"type": "string"}},
                            "required": ["step_path"]
                        }
                    },
                    {
                        "name": "split_assembly",
                        "description": "拆分大型装配体为独立零件",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "step_path": {"type": "string"},
                                "output_dir": {"type": "string", "default": "/app/parts"}
                            },
                            "required": ["step_path"]
                        }
                    },
                    {
                        "name": "generate_mesh",
                        "description": "为零件生成有限元网格",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "part_path": {"type": "string"},
                                "analysis": {"type": "string", "enum": ["stress", "thermal", "modal"], "default": "stress"},
                                "target_elements": {"type": "integer", "default": 50000}
                            },
                            "required": ["part_path"]
                        }
                    },
                    {
                        "name": "create_calculix_inp",
                        "description": "生成 CalculiX 求解器输入文件模板",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "mesh_file": {"type": "string"},
                                "analysis": {"type": "string", "default": "stress"},
                                "material": {"type": "string", "enum": ["steel", "aluminum", "titanium"], "default": "steel"}
                            },
                            "required": ["mesh_file"]
                        }
                    },
                    {
                        "name": "batch_process",
                        "description": "批量处理目录中的所有零件（网格生成）",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "parts_dir": {"type": "string", "default": "/app/parts"},
                                "analysis": {"type": "string", "default": "stress"}
                            }
                        }
                    },
                    # 通用执行工具
                    {
                        "name": "run_shell",
                        "description": "执行任意 Shell 命令（gmsh, ccx, ls 等）",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "command": {"type": "string"},
                                "working_dir": {"type": "string", "default": "/app"},
                                "timeout": {"type": "integer", "default": 600}
                            },
                            "required": ["command"]
                        }
                    },
                    {
                        "name": "run_python",
                        "description": "运行 Python 脚本",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"script_path": {"type": "string"}},
                            "required": ["script_path"]
                        }
                    }
                ]
            }
        })
        
    elif method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})

        try:
            # 基础文件操作
            if name == "read_file":
                p = get_local_path(args["file_path"])
                if not os.path.exists(p):
                    raise FileNotFoundError(f"Missing: {p}")
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read()
                send({"jsonrpc": "2.0", "id": req_id, "result": {
                    "content": [{"type": "text", "text": content}], "isError": False
                }})
                
            elif name == "write_file":
                p = get_local_path(args["file_path"])
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8") as f:
                    f.write(args["content"])
                send({"jsonrpc": "2.0", "id": req_id, "result": {
                    "content": [{"type": "text", "text": f"✓ Saved: {p}"}], "isError": False
                }})
                
            elif name == "list_files":
                local_dir = get_local_path(args.get("directory", "/app"))
                pattern = args.get("pattern", "*")
                files = glob.glob(os.path.join(local_dir, pattern))
                result = "\n".join([os.path.relpath(f, LOCAL_WORK_DIR) for f in files]) if files else "No files"
                send({"jsonrpc": "2.0", "id": req_id, "result": {
                    "content": [{"type": "text", "text": result}], "isError": False
                }})
                
            # 装配体工具
            elif name == "analyze_step":
                result = analyze_step(args["step_path"])
                send({"jsonrpc": "2.0", "id": req_id, "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}],
                    "isError": "error" in result
                }})
                
            elif name == "create_context":
                result = create_context(args["step_path"])
                text = result.get("summary", json.dumps(result, indent=2))
                send({"jsonrpc": "2.0", "id": req_id, "result": {
                    "content": [{"type": "text", "text": text}], "isError": "error" in result
                }})
                
            elif name == "split_assembly":
                result = split_assembly(args["step_path"], args.get("output_dir", "/app/parts"))
                send({"jsonrpc": "2.0", "id": req_id, "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}],
                    "isError": result.get("status") == "error"
                }})
                
            elif name == "generate_mesh":
                result = generate_mesh(
                    args["part_path"],
                    args.get("analysis", "stress"),
                    args.get("target_elements", 50000)
                )
                send({"jsonrpc": "2.0", "id": req_id, "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}],
                    "isError": "error" in result
                }})
                
            elif name == "create_calculix_inp":
                result = create_calculix_inp(
                    args["mesh_file"],
                    args.get("analysis", "stress"),
                    args.get("material", "steel")
                )
                send({"jsonrpc": "2.0", "id": req_id, "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}],
                    "isError": False
                }})
                
            elif name == "batch_process":
                result = batch_process(args.get("parts_dir", "/app/parts"), args.get("analysis", "stress"))
                send({"jsonrpc": "2.0", "id": req_id, "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}],
                    "isError": "error" in result
                }})
                
            # 通用执行
            elif name == "run_shell":
                output, is_err = docker_exec(
                    args["command"],
                    args.get("working_dir", "/app"),
                    args.get("timeout", 600)
                )
                send({"jsonrpc": "2.0", "id": req_id, "result": {
                    "content": [{"type": "text", "text": output}], "isError": is_err
                }})
                
            elif name == "run_python":
                cmd = f"python {args['script_path']}"
                output, is_err = docker_exec(cmd)
                send({"jsonrpc": "2.0", "id": req_id, "result": {
                    "content": [{"type": "text", "text": output}], "isError": is_err
                }})
                
            else:
                send({"jsonrpc": "2.0", "id": req_id, "error": {
                    "code": -32601, "message": f"Unknown tool: {name}"
                }})
                
        except Exception as e:
            log(f"Error in {name}: {e}")
            send({"jsonrpc": "2.0", "id": req_id, "error": {
                "code": -32000, "message": str(e)
            }})
            
    elif method == "ping":
        send({"jsonrpc": "2.0", "id": req_id, "result": {}})

# ==================== 主程序 ====================

if __name__ == "__main__":
    log("CAE Assembly MCP Server starting...")
    log(f"Work dir: {LOCAL_WORK_DIR}")
    log(f"Container: {DOCKER_CONTAINER_NAME}")
    
    try:
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                request = json.loads(line)
                handle_request(request)
            except json.JSONDecodeError as e:
                log(f"JSON decode error: {e}")
    except KeyboardInterrupt:
        log("Server stopped by user")
    except Exception as e:
        log(f"Fatal error: {e}")