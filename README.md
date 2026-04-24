# AI Reel Generator — Ngrok Tunnel for Mobile Access

A lightweight companion tool that creates a public tunnel to your local [AI Reel Generator](https://github.com/kausynew-afk/ai-reel-generator), so you can use it from **any mobile device, anywhere** — not just on the same WiFi.

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/kausynew-afk/ai-reel-tunnel.git
cd ai-reel-tunnel

# 2. Install dependencies
pip install -r requirements.txt

# 3. Make sure your AI Reel Generator is running on port 8000

# 4. Start the tunnel
python tunnel.py
```

A **QR code** will appear in your terminal — scan it with your phone camera to open the reel generator on mobile.

## Options

```bash
python tunnel.py                     # Default: tunnel to localhost:8000
python tunnel.py --port 3000         # Use a different port
python tunnel.py --token YOUR_TOKEN  # Use your ngrok auth token (free account)
```

## Ngrok Auth Token (Recommended)

For better reliability, get a **free** ngrok auth token:

1. Sign up at [ngrok.com](https://ngrok.com)
2. Copy your token from the dashboard
3. Run: `python tunnel.py --token YOUR_TOKEN`

Or set it as an environment variable:
```bash
set NGROK_AUTH_TOKEN=YOUR_TOKEN    # Windows
export NGROK_AUTH_TOKEN=YOUR_TOKEN  # Mac/Linux
```

## How It Works

```
┌─────────────┐     Ngrok Tunnel     ┌──────────────────┐
│  Your Phone  │ ◄══════════════════► │  Your PC         │
│  (anywhere)  │   public HTTPS URL   │  localhost:8000   │
└─────────────┘                       │  (Reel Generator) │
                                      └──────────────────┘
```

1. AI Reel Generator runs on your PC at `localhost:8000`
2. This tool creates a public ngrok tunnel
3. Scan the QR code → your phone connects to the PC through the tunnel
4. Full reel generation pipeline works from your mobile browser
