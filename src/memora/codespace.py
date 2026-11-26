import os
from memora.tools.tools import service
from pathlib import Path
import ast
import sys
import difflib
import subprocess
from dotenv import load_dotenv
import hashlib

load_dotenv()

SKIP_FILES = {"scratch_langgraph.py", "scratch_ollama.py", "test_supabase_connection.py"}
IGNORED_DIRS = {".venv", ".git", "__pycache__", "node_modules", ".pytest_cache"}
SOURCE_EXTENSIONS = {".py"}
BLOCKED={".env",".git",".venv"}

def get_file_hash(content:str):
    converted_text=content.encode("utf-8")
    file_hash=hashlib.sha256(converted_text).hexdigest()
    return file_hash



def list_source_files(root: str) -> list[Path]:
    root_path = Path(root)
    found = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [
            d for d in dirnames
            if d not in IGNORED_DIRS and not d.endswith(".egg-info")
        ]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix in SOURCE_EXTENSIONS:
                found.append(path.relative_to(root_path))

    return found


def parse_file(path: Path) -> dict:
    result = {
        "file": str(path),
        "functions": [],
        "classes": [],
        "imports": [],
    }

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError) as e:
        result["error"] = str(e)
        return result

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            result["classes"].append(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                result["imports"].append(node.module)

    return result

def summarise_file(info: dict, description: str = "") -> str:
    if "error" in info:
        return f"{info['file']} could not be parsed: {info['error']}"

    parts = []

    if info["functions"]:
        parts.append("defines functions " + ", ".join(info["functions"]))
    if info["classes"]:
        parts.append("classes " + ", ".join(info["classes"]))
    if info["imports"]:
        parts.append("imports " + ", ".join(info["imports"]))

    if not parts:
        return f"{info['file']} is empty or has no functions, classes or imports."
    pieces = [info["file"]]
    if description:
        pieces.append(description)
    pieces.append("; ".join(parts) + ".")
    return " ".join(pieces)

def index_project(root: str, name: str) -> None:
    root_path = Path(root)
    project_id = service.store.get_or_create_project(name,root_path)

    existing = [
        mem for mem in service.store.list_memories(status="active")
        if mem.project_id == project_id
    ]

    for file in list_source_files(root):
        if file.name in SKIP_FILES or "context.py" in file.parts:
            continue
        info = parse_file(root_path / file)
        info["file"] = str(file)
        description = describe_file(root_path / file)
        summary = summarise_file(info, description=description)  

        # Re-scan: archive the old memory for this file
        for mem in existing:
            if mem.content.startswith(str(file) + " "):
                service.store.archive_memory(mem.id)

        saved = service.save_memory(
            summary,
            importance=0.9,
            relevance=0.9,
            confidence=0.9,
            project_id=project_id,
            category="codebase",
        )
        print(file, "->", "saved" if saved.status else "NOT saved")

def describe_file(path:Path)->str:
    try:
        source=path.read_text(encoding="utf-8")
        context=source[:3000]
    except(UnicodeDecodeError):
        return "Could not read the file"
    if not source.strip():
        return "Empty file"
    prompt = f"""Describe this Python file for someone searching a codebase.
Answer with exactly one sentence. Mention the file's role (for example: web API, database layer, tests, configuration) and its key topics.

But do not start with the file name
File name: {path.name}


Source:
{context}

Description:

/no_think"""
    response=service.classifier.invoke(prompt)
    return response.content.split("</think>")[-1].strip()

def safe_path(root:str,user_path:str)->Path:
    root_path = Path(root).resolve()
    target = (root_path / user_path).resolve()

    if not target.is_relative_to(root_path):
        raise ValueError("Path is outside the project")

    rel = target.relative_to(root_path)
    if any(part in BLOCKED for part in rel.parts):
        raise ValueError("Path is blocked")

    return target
def read_complete_file(root: str, user_path: str) -> str:
    target = safe_path(root, user_path)   # raises ValueError if outside or blocked

    if not target.is_file():
        raise ValueError("Output is not a file")

    try:
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ValueError("Could not read the file")
    except OSError:
        raise ValueError("Could not access the file")
    

def read_file(root: str, user_path: str, max_chars: int = 8000) -> str:
    if not isinstance(max_chars, int) or isinstance(max_chars, bool):
        return "max_chars must be an integer."
    
    if max_chars<0:
        return "max_chars must be non-negative."
    try:
        path = safe_path(root, user_path)
    except ValueError as e:
        return str(e)

    if not path.is_file():
        return "Output is not a file"

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "Could not read the file"
    except OSError:
       return "Could not access the file"

    if len(text) > max_chars:
        return text[:max_chars] + "\n...[truncated]"

    return text

def generate_diff(user_path:str,old_content:str,new_content:str)->str:
    diff=difflib.unified_diff(
    old_content.splitlines(keepends=True),
    new_content.splitlines(keepends=True),
    fromfile=f"a/{user_path}",
    tofile=f"b/{user_path}"
)
    changes="".join(diff)
    return changes

def apply_edit(
    root: str,
    user_path: str,
    new_content: str,
    expected_old_hash: str
):
    temp_path = None

    try:
        target = safe_path(root, user_path)

        if not target.is_file():
            return "File does not exist"

        content = target.read_text(encoding="utf-8")
        current_hash = get_file_hash(content)

        if current_hash != expected_old_hash:
            return "File has changed since the proposal. Please generate a new proposal."

        temp_path = target.with_name(target.name + ".tmp")

        temp_path.write_text(new_content, encoding="utf-8")
        temp_path.replace(target)

    except ValueError as e:
        return str(e)

    except (OSError, UnicodeDecodeError):
        return "Could not access the file"

    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()

    return f"Successfully updated {user_path}"

def run_tests(root:str):
    root_path=Path(root).resolve()
    if not root_path.is_dir():
        return "Invalid project directory"
    try:
        result = subprocess.run(
        [sys.executable, "-m", "pytest"],
        cwd=root_path,
        capture_output=True,
        text=True,
        timeout=120
)
    except subprocess.TimeoutExpired:
        return "Tests timed out after 120 seconds"
    except OSError:
        return "Could not execute tests"
    output = result.stdout[-10000:]
    errors = result.stderr[-5000:]  
    status = "passed" if result.returncode == 0 else "failed"
    return {
        "status":status,
        "output": output,
        "errors":errors
    }

def git_diff(root):
    root_path = Path(root).resolve()

    if not root_path.is_dir():
        return "Invalid project directory"
    try:
        result = subprocess.run(["git", "diff", "HEAD"], cwd=root_path, capture_output=True, text=True,timeout=30)
    except subprocess.TimeoutExpired:
        return "Git diff timed out after 30 seconds"  
    except OSError:
        return "Could not execute Git"  
    
    output=result.stdout
    if len(output)>10000:
        output=result.stdout[-10000:]+"\n...[truncated]"

    error=result.stderr
    if result.returncode !=0:
        return error or "Git diff failed"
    return {"output":output,"error":error}


def open_vscode(root:str,user_path:str):
    try:
        path=safe_path(root,user_path)
    except ValueError as e:
        return str(e)
        

    if not path.is_file():
        return "File does not exist"
    vscode_path = os.environ.get("VSCODE_EXECUTABLE")
    
    if not vscode_path:
        return "vscode cannot open"

    if not Path(vscode_path).is_file():
        return "check the environment file variable"
    try:
        result=subprocess.Popen([vscode_path,
    str(path)
])
    except FileNotFoundError:
        return "Could not launch VS Code using the configured VSCODE_EXECUTABLE path."
        
    return f"Opened {user_path} in VScode"


    