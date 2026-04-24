"""
AI Reel Generator — Ngrok Tunnel Launcher
==========================================
Creates a public ngrok URL for the AI Reel Generator.
Reads NGROK_AUTH_TOKEN from environment variable.

Usage:
    export NGROK_AUTH_TOKEN=your_token  (or set as GitHub secret)
    python tunnel.py
    python tunnel.py --port 3000
"""

import argparse
import sys
import time
import signal
import os

try:
    from pyngrok import ngrok
except ImportError:
    print("\n[!] pyngrok is not installed. Run:  pip install pyngrok\n")
    sys.exit(1)


def start_tunnel(port):
    token = os.environ.get("NGROK_AUTH_TOKEN", "").strip()
    if not token:
        print("[ERROR] NGROK_AUTH_TOKEN environment variable is not set.")
        print("  Set it with:  export NGROK_AUTH_TOKEN=your_token")
        print("  Get a free token at: https://dashboard.ngrok.com/get-started/your-authtoken")
        sys.exit(1)

    print(f"[*] Setting ngrok auth token ({len(token)} chars)...")
    ngrok.set_auth_token(token)

    print(f"[*] Creating tunnel to localhost:{port} ...")

    try:
        tunnel = ngrok.connect(port, "http")
    except Exception as e:
        print(f"[ERROR] Failed to create tunnel: {e}")
        sys.exit(1)

    public_url = tunnel.public_url
    if public_url.startswith("http://"):
        https_url = public_url.replace("http://", "https://", 1)
    else:
        https_url = public_url

    print()
    print("=" * 55)
    print("  TUNNEL ACTIVE — COPY THIS URL TO YOUR MOBILE")
    print("=" * 55)
    print()
    print(f"  >>> {https_url}")
    print()
    print(f"  Local:  http://localhost:{port}")
    print("=" * 55)
    print()

    with open("tunnel_url.txt", "w") as f:
        f.write(https_url)

    github_step = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_step:
        with open(github_step, "a") as f:
            f.write(f"## Reel Generator Mobile URL\n\n")
            f.write(f"**Open this on your phone:**\n\n")
            f.write(f"### [{https_url}]({https_url})\n\n")
            f.write(f"Tunnel is active until you cancel this workflow.\n")

    return tunnel


def main():
    parser = argparse.ArgumentParser(
        description="AI Reel Generator — Ngrok Tunnel for Mobile Access"
    )
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    tunnel = start_tunnel(args.port)

    def shutdown(sig, frame):
        print("\n[*] Shutting down tunnel...")
        ngrok.kill()
        print("[Done]")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("[*] Tunnel running. Press Ctrl+C or cancel workflow to stop.\n")

    try:
        while True:
            time.sleep(30)
            tunnels = ngrok.get_tunnels()
            if not tunnels:
                print("[!] Tunnel dropped. Reconnecting...")
                tunnel = start_tunnel(args.port)
    except KeyboardInterrupt:
        shutdown(None, None)


if __name__ == "__main__":
    main()
