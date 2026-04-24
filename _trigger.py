import requests, subprocess, time, sys

r = subprocess.run(['git', 'credential', 'fill'], input=b'protocol=https\nhost=github.com\n\n', capture_output=True)
token = ''
for line in r.stdout.decode().split('\n'):
    if line.startswith('password='):
        token = line.split('=', 1)[1]
        break

headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github+json'}
REPO = 'kausynew-afk/ai-reel-mobile'

action = sys.argv[1] if len(sys.argv) > 1 else 'trigger'

if action == 'trigger':
    resp = requests.post(
        f'https://api.github.com/repos/{REPO}/actions/workflows/launch.yml/dispatches',
        headers=headers,
        json={'ref': 'master', 'inputs': {'duration_minutes': '30'}}
    )
    print(f"Trigger: {resp.status_code}")

elif action == 'status':
    resp = requests.get(f'https://api.github.com/repos/{REPO}/actions/runs?per_page=1', headers=headers)
    run = resp.json()['workflow_runs'][0]
    run_id = run['id']
    print(f"Run: {run_id} | Status: {run['status']} | Conclusion: {run.get('conclusion', '-')}")

    resp2 = requests.get(f'https://api.github.com/repos/{REPO}/actions/runs/{run_id}/jobs', headers=headers)
    for job in resp2.json().get('jobs', []):
        for step in job.get('steps', []):
            c = step.get('conclusion', 'running')
            icon = {'success': 'OK', 'failure': 'FAIL', 'skipped': 'SKIP'}.get(c, '..')
            print(f"  [{icon}] {step['name']}")

elif action == 'logs':
    import zipfile, io
    resp = requests.get(f'https://api.github.com/repos/{REPO}/actions/runs?per_page=1', headers=headers)
    run_id = resp.json()['workflow_runs'][0]['id']
    log_resp = requests.get(f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/logs", headers=headers)
    if log_resp.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(log_resp.content))
        target = sys.argv[2] if len(sys.argv) > 2 else 'Test script'
        for name in z.namelist():
            if target.lower() in name.lower():
                content = z.read(name).decode('utf-8', errors='replace')
                for ln in content.split('\n'):
                    clean = ln.encode('ascii', 'replace').decode().rstrip()
                    # Strip ANSI color codes
                    import re
                    clean = re.sub(r'\x1b\[[0-9;]*m', '', clean)
                    clean = re.sub(r'\[36;1m|\[0m', '', clean)
                    if clean.strip():
                        print(clean[:250])
