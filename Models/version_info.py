#!/usr/bin/env python3
import os
import glob
import ast
import json
import importlib
from importlib import metadata

def find_py_and_ipynb():
    return glob.glob("*.py") + glob.glob("*.ipynb")

def extract_imports_py(path):
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module.split(".")[0]

def extract_imports_ipynb(path):
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    yield alias.name.split(".")[0]
            elif isinstance(node, ast.ImportFrom) and node.module:
                yield node.module.split(".")[0]

def collect_all_modules(files):
    mods = set()
    for fn in files:
        if fn.endswith(".py"):
            mods.update(extract_imports_py(fn))
        else:
            mods.update(extract_imports_ipynb(fn))
    return {m for m in mods if m}  # drop empty

def is_third_party(module_name):
    """
    Try to import the module. If its file path lives in
    site-packages or dist-packages, treat it as third-party.
    """
    try:
        mod = importlib.import_module(module_name)
    except ImportError:
        return False
    path = getattr(mod, "__file__", "") or ""
    return ("site-packages" in path) or ("dist-packages" in path)

def get_version(pkg):
    try:
        return metadata.version(pkg)
    except metadata.PackageNotFoundError:
        return "NOT FOUND"
    except Exception:
        return "UNKNOWN"

def main():
    files = find_py_and_ipynb()
    modules = collect_all_modules(files)

    results = []
    for mod in sorted(modules, key=str.lower):
        if not is_third_party(mod):
            # skip stdlib and local modules
            continue
        ver = get_version(mod)
        results.append(f"{mod}=={ver}")

    out_file = "requirements_versions.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    print(f"Wrote {len(results)} entries to {out_file}")

if __name__ == "__main__":
    main()