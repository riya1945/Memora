import os
from pathlib import Path
import ast

IGNORED_DIRS = {".venv", ".git", "__pycache__", "node_modules", ".pytest_cache"}
SOURCE_EXTENSIONS = {".py"}


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

def summarise_file(info: dict) -> str:
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

    return f"{info['file']} " + "; ".join(parts) + "."
