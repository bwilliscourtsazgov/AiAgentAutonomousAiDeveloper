from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path

from src.common.config import coder_log_dir, logs_dir
from src.common.fs_utils import ensure_dir


def append_event(ai_root: Path, agent: str, event: str, instruction_name: str, stage: str, details: dict[str, str] | None = None) -> Path:
    event_details = details or {}
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = {"timestamp_utc": timestamp, "agent": agent, "event": event, "instruction_name": instruction_name, "stage": stage, "details": event_details}
    ensure_dir(logs_dir(ai_root))
    log_file = logs_dir(ai_root) / "agent-history.log"
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")
    append_html_event(ai_root, timestamp, instruction_name, stage, event_details)
    return log_file


def append_html_event(ai_root: Path, event_time: str, instruction_name: str, stage: str, details: dict[str, str]) -> Path:
    folder = coder_log_dir(ai_root)
    ensure_dir(folder)
    now = datetime.now()
    html_file = folder / ("Log_" + now.strftime("%Y%m%d") + ".html")
    message_type = stage if stage in {"IN", "PROCESSING", "FAILURE", "SUCCESS"} else ("QA" if stage == "AIAgentQA_IN" else "INFORMATION")
    message = stage + ": " + str(details)
    if not html_file.exists():
        html_file.write_text("<html><body><table border=1><tr><th>Date</th><th>File Name</th><th>Message</th><th>Message Type</th></tr>\n", encoding="utf-8")
    style = "color: red; font-weight: bold;" if message_type == "FAILURE" else ("color: green; font-weight: bold;" if message_type == "SUCCESS" else "color: black; font-weight: normal;")
    row = "<tr><td>" + escape(event_time) + "</td><td>" + escape(instruction_name) + "</td><td>" + escape(message) + "</td><td style=\"" + style + "\">" + message_type + "</td></tr>\n"
    with html_file.open("a", encoding="utf-8") as handle:
        handle.write(row)
    return html_file
