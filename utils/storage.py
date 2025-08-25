# utils/storage.py
# 作用：用 JSON 文件保存/读取数据（线程安全）
# Purpose: save/load small dicts to a JSON file (thread-safe)

from __future__ import annotations
import json, os, threading
from typing import Any, Dict

_LOCKS: dict[str, threading.Lock] = {}

def _get_lock(path: str) -> threading.Lock:
    if path not in _LOCKS:
        _LOCKS[path] = threading.Lock()
    return _LOCKS[path]

def ensure_parent(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

def load_json(path: str, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ensure_parent(path)
    lock = _get_lock(path)
    with lock:
        if not os.path.exists(path):
            return default or {}
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default or {}

def save_json(path: str, data: Dict[str, Any]) -> None:
    ensure_parent(path)
    lock = _get_lock(path)
    tmp = path + ".tmp"
    with lock:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
