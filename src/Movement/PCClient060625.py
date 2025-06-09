#!/usr/bin/env python3
"""PC-side client for GolfBot (updated to match the 2025 EV3 server API).

Keys (case-insensitive):
    W – drive forward
    S – turn right
    A – turn left
    V – open gate
    C – close gate
    P – push out (ball)
    R – push return (retract pusher)
    X – *immediate* stop of drive base
    Q – quit the program

Adjust ``EV3_IP`` as needed for your network.
"""

from __future__ import annotations

import socket

EV3_IP = "192.168.199.36"   # ← IP address of your brick
PORT = 5532                  # Must match the server’s port

HELLO_SCRIPT = 'print("Hello from PC Client")\n'

# --- movement parameters ----------------------------------------------
FORWARD_MM = 500    # positive = forward (edit to suit)
TURN_DEG   = 45     # degrees to turn with A/S keys

# ----------------------------------------------------------------------
# Networking helper
# ----------------------------------------------------------------------

def send_and_receive(script: str) -> str:
    """Send *script* to the EV3 and return its textual reply."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((EV3_IP, PORT))
        sock.sendall(script.encode("utf-8"))
        # signal end-of-transmission so the brick can reply
        sock.shutdown(socket.SHUT_WR)

        chunks: list[bytes] = []
        while chunk := sock.recv(1024):
            chunks.append(chunk)
    return b"".join(chunks).decode("utf-8")

# ----------------------------------------------------------------------
# Key → command mapper
# ----------------------------------------------------------------------

def build_command(key: str) -> str:
    k = key.lower()
    if k == "w":
        return f"drive_straight_mm({FORWARD_MM})\n"
    if k == "s":
        return f"turn_right_deg({TURN_DEG})\n"
    if k == "a":
        return f"turn_left_deg({TURN_DEG})\n"
    if k == "v":
        return "open_gate()\n"
    if k == "c":
        return "close_gate()\n"
    if k == "p":
        return "push_out()\n"
    if k == "r":
        return "push_return()\n"
    if k == "x":
        return "golfbot.stop()\n"
    # default: say hello so we always send *something*
    return HELLO_SCRIPT

# ----------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------

def main() -> None:
    print(
        "Press keys:\n"
        "  W – forward   S – right   A – left\n"
        "  V – open gate C – close gate\n"
        "  P – push out  R – push return\n"
        "  X – STOP      Q – quit\n"
    )
    while True:
        key = input("> ").strip()
        if key.lower() == "q":
            break
        script = build_command(key)
        reply = send_and_receive(script)
        print("EV3:", reply)


if __name__ == "__main__":
    main()