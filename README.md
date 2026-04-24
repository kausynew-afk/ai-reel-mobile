# AI Reel Generator — Mobile Access

Run the [AI Reel Generator](https://github.com/kausynew-afk/ai-reel-generator) from your phone using GitHub Actions + Ngrok tunnel.

## How to Use (From Your Phone)

### One-time Setup

1. Get a **free** ngrok auth token at [ngrok.com](https://ngrok.com)
2. Go to this repo's **Settings → Secrets → Actions**
3. Add a secret: Name = `NGROK_AUTH_TOKEN`, Value = your token

### Launch the Server

1. Open this repo on your phone (GitHub app or browser)
2. Go to **Actions** tab
3. Click **"Launch Reel Generator for Mobile"**
4. Click **"Run workflow"** → choose duration → **Run**
5. Open the running workflow → look for the **URL** in the logs
6. Open that URL on your phone — the full Reel Generator is ready!

### When Done

Cancel the workflow to stop the server, or it auto-stops after the chosen duration.

## How It Works

```
┌─────────────┐     Ngrok Tunnel     ┌───────────────────────┐
│  Your Phone  │ ◄══════════════════► │  GitHub Actions Runner │
│  (browser)   │   public HTTPS URL   │  (Reel Generator)      │
└─────────────┘                       └───────────────────────┘
```

1. GitHub Actions spins up a cloud server
2. Installs Python, FFmpeg, and all dependencies
3. Starts the AI Reel Generator on the runner
4. Creates an ngrok tunnel → gives you a public URL
5. You open the URL on your phone and create reels

## Local Usage

You can also run the tunnel locally on your PC:

```bash
pip install -r requirements.txt
python tunnel.py --token YOUR_NGROK_TOKEN
```
