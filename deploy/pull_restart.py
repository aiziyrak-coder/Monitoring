"""Git pull + restart backend."""
import sys, time
try:
    import paramiko
except ImportError:
    print("pip install paramiko"); sys.exit(1)

PASSWORD = "Ziyrak2025Ai"
HOST = "167.71.53.238"
USER = "root"
APP = "/opt/clinicmonitoring/backend"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Ulanish: {USER}@{HOST}")
client.connect(HOST, username=USER, password=PASSWORD, timeout=30)

def run(cmd, label='', timeout=120):
    if label:
        print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors='replace').strip()
    err = stderr.read().decode(errors='replace').strip()
    if out: print(out[:1500].encode('ascii', errors='replace').decode())
    if err and 'deprecat' not in err.lower() and 'warn' not in err.lower():
        print('[ERR]', err[:400].encode('ascii', errors='replace').decode())
    return out

run(f"cd {APP} && git pull origin main 2>&1 | tail -5", "Git pull")
run("systemctl restart clinicmonitoring-backend", "Restart")
time.sleep(6)
run("systemctl is-active clinicmonitoring-backend", "Status")
time.sleep(15)
run("journalctl -u clinicmonitoring-backend -n 30 --no-pager 2>&1 | grep -E 'HL7|onlayn|socket' | tail -10", "HL7 loglar")
run("curl -s http://127.0.0.1:8010/api/health 2>&1", "Health")

client.close()
print("\nTayyor!")
