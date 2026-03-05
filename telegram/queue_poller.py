"""
telegram/queue_poller.py (Updated for Task 3.2)

- Adds local whitelist check via security.py
- Adds 5-minute timeout failsafe via wait_for_human_approval()
"""

import os
import json
import time
import requests
from dotenv import load_dotenv
from .security import is_authorized

load_dotenv()

VERCEL_QUEUE_URL = os.getenv("VERCEL_QUEUE_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
LOCAL_COMMAND_FILE = os.path.join(os.path.dirname(__file__), '..', 'command_queue.json')
POLL_INTERVAL_SECONDS = 30
VALID_COMMANDS = {"APPROVE", "SKIP", "PAUSE", "STATUS", "RESUME"}


def send_telegram_message(chat_id: int, text: str):
    """Sends a message back to the operator via the Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN:
        print("[BOT] TELEGRAM_BOT_TOKEN not set. Cannot send message.")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=5)
    except Exception as e:
        print(f"[BOT] Failed to send Telegram message: {e}")


def fetch_commands_from_cloud() -> list:
    """Polls the Vercel cloud queue, returns and clears pending commands."""
    if not VERCEL_QUEUE_URL:
        return []
    try:
        response = requests.get(f"{VERCEL_QUEUE_URL}/api/get_commands", timeout=10)
        response.raise_for_status()
        return response.json().get("commands", [])
    except Exception as e:
        print(f"[POLLER] Failed to fetch commands: {e}")
        return []


def _read_local_queue() -> list:
    """Reads the local command queue JSON file."""
    if os.path.exists(LOCAL_COMMAND_FILE):
        with open(LOCAL_COMMAND_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def _write_local_queue(queue: list):
    """Writes to the local command queue JSON file."""
    with open(LOCAL_COMMAND_FILE, 'w') as f:
        json.dump(queue, f, indent=2)


def wait_for_human_approval(job_info: dict, operator_chat_id: int, timeout_seconds: int = 300) -> str:
    """
    Sends a HITL prompt to the operator and waits up to `timeout_seconds` for a response.
    Returns the operator's command (e.g., 'APPROVE', 'SKIP'), or 'SKIP' if timeout expires.
    """
    prompt = (
        f"🤖 AutoClaw needs your decision!\n\n"
        f"🏢 *{job_info.get('company', 'Unknown')}* — {job_info.get('title', 'Unknown')}\n\n"
        f"Reply with:\n✅ APPROVE — to apply\n⏭️ SKIP — to skip\n\n"
        f"⏳ Auto-skipping in {timeout_seconds // 60} minutes if no response."
    )
    send_telegram_message(operator_chat_id, prompt)
    print(f"[HITL] Waiting up to {timeout_seconds}s for operator response...")

    start_time = time.time()
    check_interval = 10  # seconds between local queue polls

    while time.time() - start_time < timeout_seconds:
        time.sleep(check_interval)

        # Also fetch from cloud in case the poller hasn't run yet
        cloud_commands = fetch_commands_from_cloud()
        for cmd in cloud_commands:
            process_command(cmd)  # writes to local queue

        # Check local queue for an APPROVE or SKIP
        pending = _read_local_queue()
        for i, entry in enumerate(pending):
            if entry.get("command") in ("APPROVE", "SKIP"):
                # Consume the command and return it
                pending.pop(i)
                _write_local_queue(pending)
                decision = entry["command"]
                send_telegram_message(operator_chat_id, f"✅ Got it! Decision: *{decision}*")
                print(f"[HITL] Operator responded: {decision}")
                return decision

    # Timeout reached — auto-skip
    print("[HITL] Timeout reached. Auto-skipping job.")
    send_telegram_message(operator_chat_id, "⏰ Timeout! No response received. Auto-skipping this job.")
    return "SKIP"


def process_command(command: dict):
    """Processes a cloud command after whitelist check, writes to local queue."""
    user_id = command.get("user_id")
    text = command.get("text", "").strip().upper()
    username = command.get("username", "unknown")

    # ── Security Gate ──────────────────────────────────────
    if not is_authorized(user_id):
        print(f"[SECURITY] Dropped unauthorized command from user_id={user_id} (@{username})")
        return
    # ───────────────────────────────────────────────────────

    if text not in VALID_COMMANDS:
        print(f"[POLLER] Ignoring unknown command '{text}' from @{username}")
        return

    print(f"[POLLER] Processing command '{text}' from @{username}")
    pending = _read_local_queue()
    pending.append({
        "command": text,
        "from_user": username,
        "user_id": user_id,
        "chat_id": command.get("chat_id"),
        "received_at": command.get("received_at"),
        "processed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    _write_local_queue(pending)
    print(f"[POLLER] Command '{text}' written to local queue.")


def run_poller():
    """Main polling loop — fetches cloud queue every POLL_INTERVAL_SECONDS."""
    print(f"[POLLER] AutoClaw queue poller started. Polling every {POLL_INTERVAL_SECONDS}s.")
    while True:
        commands = fetch_commands_from_cloud()
        if commands:
            print(f"[POLLER] {len(commands)} new command(s) found.")
            for cmd in commands:
                process_command(cmd)
        else:
            print(f"[POLLER] Queue empty. Next check in {POLL_INTERVAL_SECONDS}s...")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_poller()
