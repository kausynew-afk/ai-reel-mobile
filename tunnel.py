"""
AI Reel Generator — Ngrok Tunnel Launcher
==========================================
Run this on your PC to create a public URL for the AI Reel Generator.
Then open the URL on any mobile device to use the reel generator remotely.

Usage:
    python tunnel.py                     # Tunnel to localhost:8000 (default)
    python tunnel.py --port 3000         # Tunnel to a different port
    python tunnel.py --token YOUR_TOKEN  # Use your own ngrok auth token
"""

import argparse
import sys
import time
import signal
import os

try:
    from pyngrok import ngrok, conf
except ImportError:
    print("\n[!] pyngrok is not installed. Run:\n")
    print("    pip install -r requirements.txt\n")
    sys.exit(1)

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║       AI Reel Generator — Mobile Access      ║
╠══════════════════════════════════════════════╣
║  Creates a public tunnel to your local       ║
║  Reel Generator so you can use it from       ║
║  any mobile device, anywhere.                ║
╚══════════════════════════════════════════════╝
    """)


def print_qr_terminal(url):
    """Print QR code directly in the terminal."""
    if not HAS_QRCODE:
        print(f"  [TIP] Install 'qrcode' for terminal QR:  pip install qrcode[pil]\n")
        return

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Print using unicode block characters
    matrix = qr.get_matrix()
    for r in range(0, len(matrix) - 1, 2):
        line = "  "
        for c in range(len(matrix[r])):
            top = matrix[r][c]
            bot = matrix[r + 1][c] if r + 1 < len(matrix) else False
            if top and bot:
                line += "█"
            elif top and not bot:
                line += "▀"
            elif not top and bot:
                line += "▄"
            else:
                line += " "
        print(line)
    print()


def start_tunnel(port, token):
    clear_screen()
    print_banner()

    if token:
        print(f"  [*] Setting ngrok auth token...")
        ngrok.set_auth_token(token)

    print(f"  [*] Starting tunnel to localhost:{port} ...")
    print()

    try:
        tunnel = ngrok.connect(port, "http")
    except Exception as e:
        error_msg = str(e)
        if "certificate" in error_msg.lower() or "tls" in error_msg.lower():
            print("  [!] SSL/TLS error detected (common on corporate networks).")
            print("  [!] Try one of these:")
            print("      1. Run on a personal WiFi network")
            print("      2. Use --token with a free ngrok account (https://ngrok.com)")
            print()
        print(f"  [ERROR] {error_msg}")
        sys.exit(1)

    public_url = tunnel.public_url
    if public_url.startswith("http://"):
        https_url = public_url.replace("http://", "https://", 1)
    else:
        https_url = public_url

    clear_screen()
    print_banner()

    print("  ✓ TUNNEL IS ACTIVE")
    print("  " + "─" * 44)
    print()
    print(f"  Public URL:  {https_url}")
    print(f"  Local:       http://localhost:{port}")
    print()
    print("  " + "─" * 44)
    print("  Scan QR code with your phone camera:")
    print()

    print_qr_terminal(https_url)

    if not HAS_QRCODE:
        qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={https_url}"
        print(f"  QR Code image: {qr_api_url}")
        print()

    print("  " + "─" * 44)
    print("  Press Ctrl+C to stop the tunnel")
    print("  " + "─" * 44)
    print()

    return tunnel


def main():
    parser = argparse.ArgumentParser(
        description="AI Reel Generator — Ngrok Tunnel for Mobile Access"
    )
    parser.add_argument(
        "--port", type=int, default=8000,
        help="Local port where AI Reel Generator is running (default: 8000)"
    )
    parser.add_argument(
        "--token", type=str, default=None,
        help="Ngrok auth token (get free at https://ngrok.com)"
    )
    args = parser.parse_args()

    token = args.token or os.environ.get("NGROK_AUTH_TOKEN")

    tunnel = start_tunnel(args.port, token)

    def shutdown(sig, frame):
        print("\n\n  [*] Shutting down tunnel...")
        ngrok.kill()
        print("  [✓] Tunnel closed. Goodbye!\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(None, None)


if __name__ == "__main__":
    main()
