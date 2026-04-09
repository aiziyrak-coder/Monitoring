"""Build frontend va health tekshirish."""
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
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors='replace', ).strip()
    err = stderr.read().decode(errors='replace').strip()
    if out: print(out[:1500].encode('ascii', errors='replace').decode())
    if err and 'deprecat' not in err.lower() and 'warn' not in err.lower():
        print('[ERR]', err[:400].encode('ascii', errors='replace').decode())
    return out

# Frontend build
run(f"cd {APP}/frontend && npm run build 2>&1 | tail -5", "Frontend build", timeout=240)
run("nginx -s reload", "Nginx reload")
time.sleep(3)

# Check HL7 + health
run("curl -s http://127.0.0.1:8010/api/health 2>&1", "Health")
run("journalctl -u clinicmonitoring-backend -n 30 --no-pager 2>&1 | grep -E 'HL7|onlayn|socket|qurilma' | tail -15", "HL7 loglar")

client.close()
print("\nTayyor!")
