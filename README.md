# AI Reel Generator — Mobile Access

Run the [AI Reel Generator](https://github.com/kausynew-afk/ai-reel-generator) from your phone using GitHub Actions + Cloudflare Tunnel.

**No signup. No tokens. No secrets. Just run the workflow.**

## How to Use (From Your Phone)

1. Open this repo on your phone (GitHub app or browser)
2. Go to **Actions** tab
3. Click **"Launch Reel Generator for Mobile"**
4. Click **"Run workflow"** → choose duration → **Run**
5. Open the running workflow → find the **URL** in the logs or in the **Summary**
6. Open that URL on your phone — the full Reel Generator is ready!

### When Done

Cancel the workflow to stop the server, or it auto-stops after the chosen duration.

## How It Works

```
┌─────────────┐   Cloudflare Tunnel   ┌───────────────────────┐
│  Your Phone  │ ◄═══════════════════► │  GitHub Actions Runner │
│  (browser)   │   public HTTPS URL    │  (Reel Generator)      │
└─────────────┘                        └───────────────────────┘
```

1. GitHub Actions spins up a cloud server
2. Installs Python, FFmpeg, and all Reel Generator dependencies
3. Starts the AI Reel Generator on the runner
4. Creates a Cloudflare Tunnel → gives you a free public HTTPS URL
5. You open the URL on your phone and create reels

No ngrok account needed. No auth tokens. Completely free.
