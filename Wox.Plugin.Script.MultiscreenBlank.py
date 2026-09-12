#!/usr/bin/env python3
# {
#   "Id": "93944b05-014b-4c03-90a2-f34562304ecb",
#   "Name": "Multiscreen Blank",
#   "Author": "Flartiny",
#   "Version": "1.0.0",
#   "MinWoxVersion": "2.0.0",
#   "Description": "通过命令行控制 Multiscreen Blank 显示器遮罩",
#   "Icon": "emoji:⬛",
#   "TriggerKeywords": ["msb"],
#   "SupportedOS": ["Windows"],
#   "SettingDefinitions": [
#     {
#       "Type": "textbox",
#       "Value": {
#         "Key": "executable_path",
#         "Label": "Multiscreen Blank 可执行文件",
#         "Tooltip": "MultiscreenBlank2.exe 的完整路径。留空时自动使用默认安装路径。",
#         "DefaultValue": "",
#         "MaxLines": 1,
#         "Style": { "Width": 560 }
#       },
#       "IsPlatformSpecific": true
#     }
#   ]
# }

"""Wox Script Plugin：直接调用 Multiscreen Blank 的公开命令行接口。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_EXECUTABLE = Path(
    r"C:\Program Files\Nookkin\MultiscreenBlank2\MultiscreenBlank2.exe"
)
LOG_FILE = Path(__file__).with_suffix(".log")

OPERATIONS = (
    ("blank-all", "遮罩全部显示器", "/blank", "all", "⬛"),
    ("blank-current", "遮罩鼠标所在显示器", "/blank", "current", "🖱️"),
    ("reveal-all", "取消全部显示器遮罩", "/reveal", "all", "⬜"),
)


def log(message: str) -> None:
    """将查询和操作轨迹记录到脚本同目录，方便无需 Python Host 即可排障。"""
    timestamp = datetime.now(UTC).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with LOG_FILE.open("a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] {message}\n")
    except OSError:
        return


def executable_path() -> Path | None:
    configured = os.getenv("WOX_SETTING_EXECUTABLE_PATH", "").strip().strip('"')
    if configured:
        candidate = Path(configured).expanduser()
        return candidate if candidate.is_file() else None

    if DEFAULT_EXECUTABLE.is_file():
        return DEFAULT_EXECUTABLE

    return None


def result_item(
    operation_id: str, title: str, operation: str, selector: str, icon: str
) -> dict[str, Any]:
    return {
        "title": title,
        "subtitle": f"执行：MultiscreenBlank2.exe {operation} {selector}",
        "icon": f"emoji:{icon}",
        "score": 100 if operation_id == "blank-all" else 90,
        "actions": [
            {
                "id": operation_id,
                "name": "执行",
                "icon": f"emoji:{icon}",
                "data": {"operation": operation, "selector": selector},
            }
        ],
    }


def parse_display_name(params: dict[str, Any]) -> str | None:
    """将 `msb <显示器名>` 解析为要遮罩的显示器名称。"""
    raw_query = str(params.get("raw_query", "")).strip()
    trigger_keyword = str(params.get("trigger_keyword", "")).strip()
    if not raw_query or not trigger_keyword:
        return None

    if not raw_query.casefold().startswith(trigger_keyword.casefold()):
        return None

    display_name = raw_query[len(trigger_keyword) :].strip()
    return display_name or None


def display_name_result(display_name: str) -> dict[str, Any]:
    return {
        "title": f"切换显示器遮罩：{display_name}",
        "subtitle": f'执行：MultiscreenBlank2.exe /toggle name "{display_name}"',
        "icon": "emoji:🎯",
        "score": 120,
        "actions": [
            {
                "id": "toggle-by-name",
                "name": "切换",
                "icon": "emoji:🎯",
                "data": {"display_name": display_name},
            }
        ],
    }


def query_response(params: dict[str, Any], request_id: Any) -> dict[str, Any]:
    display_name = parse_display_name(params)

    executable = executable_path()
    if executable is None:
        log("query: executable not found")
        items = [
            {
                "title": "未找到 MultiscreenBlank2.exe",
                "subtitle": "请在脚本插件设置中配置 executable_path",
                "icon": "emoji:⚠️",
                "score": 100,
            }
        ]
    elif display_name:
        log(f"query: executable={executable}; display_name={display_name}")
        items = [display_name_result(display_name)]
    else:
        log(f"query: executable={executable}")
        items = [result_item(*item) for item in OPERATIONS]

    return {"jsonrpc": "2.0", "result": {"items": items}, "id": request_id}


def action_response(params: dict[str, Any], request_id: Any) -> dict[str, Any]:
    executable = executable_path()
    action_id = str(params.get("id", ""))
    raw_data = params.get("data", {})
    if isinstance(raw_data, str):
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            data = {}
    else:
        data = raw_data if isinstance(raw_data, dict) else {}

    if executable is None:
        message = "未找到 MultiscreenBlank2.exe；请配置 executable_path。"
        log(f"action {action_id}: {message}")
        return {
            "jsonrpc": "2.0",
            "result": {"action": "notify", "message": message},
            "id": request_id,
        }

    if action_id == "toggle-by-name":
        display_name = data.get("display_name")
        if not isinstance(display_name, str) or not display_name.strip():
            message = "显示器名称缺失。"
            log(f"action {action_id}: {message}; data={raw_data!r}")
            return {
                "jsonrpc": "2.0",
                "result": {"action": "notify", "message": message},
                "id": request_id,
            }
        command = [str(executable), "/toggle", "name", display_name]
    else:
        operation = data.get("operation")
        selector = data.get("selector")
        if not isinstance(operation, str) or not isinstance(selector, str):
            message = f"操作参数缺失：{action_id}"
            log(f"action {action_id}: {message}; data={raw_data!r}")
            return {
                "jsonrpc": "2.0",
                "result": {"action": "notify", "message": message},
                "id": request_id,
            }
        command = [str(executable), operation, selector]

    try:
        subprocess.Popen(
            command,
            close_fds=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except OSError as error:
        message = f"启动失败：{error}"
        log(f"action {action_id}: {message}; command={command!r}")
        return {
            "jsonrpc": "2.0",
            "result": {"action": "notify", "message": message},
            "id": request_id,
        }

    message = f"已发送：{' '.join(command)}"
    log(f"action {action_id}: {message}")
    return {
        "jsonrpc": "2.0",
        "result": {"action": "notify", "message": message},
        "id": request_id,
    }


def main() -> int:
    try:
        request = json.loads(sys.stdin.read())
    except json.JSONDecodeError as error:
        print(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": str(error)},
                    "id": None,
                },
                ensure_ascii=False,
            )
        )
        return 1

    params = request.get("params", {})
    request_id = request.get("id")
    method = request.get("method")

    if method == "query":
        response = query_response(
            params if isinstance(params, dict) else {}, request_id
        )
    elif method == "action":
        response = action_response(
            params if isinstance(params, dict) else {}, request_id
        )
    else:
        response = {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Unsupported method: {method}"},
            "id": request_id,
        }

    print(json.dumps(response, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
