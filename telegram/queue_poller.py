"""
telegram/queue_poller.py

Local Python script that decouples AutoClaw from Telegram's direct connection.
Purpose: Every 30 seconds, polls the Vercel cloud queue endpoint to check for 
         pending commands sent while the laptop was offline or busy. This solves 
         the "Sleeping Laptop" failure mode.

Commands handled: APPROVE, SKIP, PAUSE, STATUS
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# The public URL of your deployed Vercel queue endpoint
VERCEL_QUEUE_URL = os.getenv("VERCEL_QUEUE_URL", "")

# Local file that the main AutoClaw engine reads to pick up operator decisions
LOCAL_COMMAND_FILE = os.path.join(os.path.dirname(__file__), '..', 'command_queue.json')

# How often to poll the cloud queue (seconds)
POLL_INTERVAL_SECONDS = 30

# Valid commands the system understands
VALID_COMMANDS = {"APPROVE", "SKIP", "PAUSE", "STATUS", "RESUME"}


def fetch_commands_from_cloud() -> list:
    """
    Makes a GET request to the Vercel endpoint and retrieves pending commands.
    The cloud queue is automatically cleared after this call.
    """
    if not VERCEL_QUEUE_URL:
        print("[POLLER] ERROR: VERCEL_QUEUE_URL is not set in .env. Cannot poll.")
        return []

    try:
        response = requests.get(f"{VERCEL_QUEUE_URL}/api/get_commands", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("commands", [])
    except requests.exceptions.ConnectionError:
        print("[POLLER] Could not reach cloud queue. Check internet connection.")
        return []
    except Exception as e:
        print(f"[POLLER] Failed to fetch commands: {e}")
        return []


def process_command(command: dict):
    """
    Processes a single command from the queue and writes it to the local 
    command file for the AutoClaw engine to act on.
    """
    text = command.get("text", "").strip().upper()
    username = command.get("username", "unknown")

    # Only act on recognized commands
    if text not in VALID_COMMANDS:
        print(f"[POLLER] Ignoring unknown command '{text}' from @{username}")
        return

    print(f"[POLLER] Processing command '{text}' from @{username}")

    # Write the command to the local file
    pending = []
    if os.path.exists(LOCAL_COMMAND_FILE):
        with open(LOCAL_COMMAND_FILE, 'r') as f:
            try:
                pending = json.load(f)
            except json.JSONDecodeError:
                pending = []

    pending.append({
        "command": text,
        "from_user": username,
        "chat_id": command.get("chat_id"),
        "received_at": command.get("received_at"),
        "processed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })

    with open(LOCAL_COMMAND_FILE, 'w') as f:
        json.dump(pending, f, indent=2)

    print(f"[POLLER] Command '{text}' written to local queue.")


def run_poller():
    """
    Main loop. Polls the cloud queue every POLL_INTERVAL_SECONDS.
    """
    print(f"[POLLER] AutoClaw queue poller started. Polling every {POLL_INTERVAL_SECONDS}s.")
    print(f"[POLLER] Cloud endpoint: {VERCEL_QUEUE_URL}")
    print(f"[POLLER] Local command file: {os.path.abspath(LOCAL_COMMAND_FILE)}")
    print("-" * 50)

    while True:
        commands = fetch_commands_from_cloud()

        if commands:
            print(f"[POLLER] {len(commands)} new command(s) found in queue.")
            for cmd in commands:
                process_command(cmd)
        else:
            print(f"[POLLER] No pending commands. Next check in {POLL_INTERVAL_SECONDS}s...")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_poller()
