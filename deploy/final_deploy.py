"""Final deploy: git pull + frontend build + restart."""
import sys, time
try:
    import paramiko
except ImportError:
    print("pip install paramiko"); sys.exit(1)

PASSWORD = "Ziyrak2025Ai"
HOST = "167.71.53.238"
USER = "root"
APP = "/opt/clinicmonitoring"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Ulanish: {USER}@{HOST}")
client.connect(HOST, username=USER, password=PASSWORD, timeout=60)

def run(cmd, label='', timeout=300):
    if label:
        print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout, get_pty=False)
    stdout.channel.settimeout(timeout)
    out = stdout.read().decode(errors='replace').strip()
    err = stderr.read().decode(errors='replace').strip()
    if out: print(out[:2000])
    if err and 'deprecat' not in err.lower() and 'warn' not in err.lower():
        print('[ERR]', err[:400])
    return out

run(f"cd {APP}/backend && timeout 60 git pull origin main 2>&1 | tail -5", "Git pull")
run(f"cd {APP}/backend && .venv/bin/python manage.py migrate --noinput 2>&1", "Migrate")
run("systemctl restart clinicmonitoring-backend", "Backend restart")
time.sleep(5)
run("systemctl is-active clinicmonitoring-backend", "Status")

# Frontend build
run(f"cd {APP}/frontend && npm run build 2>&1 | tail -8", "Frontend build", timeout=180)
run("nginx -s reload", "Nginx reload")

time.sleep(8)
run('curl -s http://127.0.0.1:8010/api/health', "Health")
run('journalctl -u clinicmonitoring-backend -n 20 --no-pager | grep -E "HL7|qurilma|onlayn|socket" | tail -10', "HL7 loglar")

client.close()
print("\nDeploy tugadi!")
