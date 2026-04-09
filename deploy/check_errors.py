"""Backend xatolarini ko'rish."""
import sys, time
try:
    import paramiko
except ImportError:
    print("pip install paramiko"); sys.exit(1)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('167.71.53.238', username='root', password='Ziyrak2025Ai', timeout=30)

def run(cmd, label='', timeout=60):
    if label: print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors='replace').strip()
    if out: print(out[:3000].encode('ascii', errors='replace').decode())
    return out

# Barcha loglar — xato va warning larni ko'rish
run("journalctl -u clinicmonitoring-backend -n 100 --no-pager 2>&1 | grep -iE 'error|exception|traceback|warning|ERROR|WARN' | tail -30", "Backend xatolar")
run("journalctl -u clinicmonitoring-backend -n 80 --no-pager 2>&1 | tail -40", "Oxirgi 80 log")

client.close()
