"""Backend restart + HL7 tekshiruv."""
import sys, time
try:
    import paramiko
except ImportError:
    print("pip install paramiko"); sys.exit(1)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('167.71.53.238', username='root', password='Ziyrak2025Ai', timeout=30)

def run(cmd, label=''):
    if label:
        print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors='replace').strip()
    err = stderr.read().decode(errors='replace').strip()
    if out:
        print(out)
    if err and 'deprecat' not in err.lower() and 'warn' not in err.lower():
        print('[ERR]', err[:400])
    return out

run('systemctl restart clinicmonitoring-backend', 'Backend restart')
time.sleep(6)
run('systemctl is-active clinicmonitoring-backend', 'Status')
run('curl -s http://127.0.0.1:8010/api/health', 'Health')
time.sleep(10)
run('journalctl -u clinicmonitoring-backend -n 30 --no-pager | grep -E "HL7|qurilma|device|peer" | tail -15', 'HL7 loglar (restart keyin)')

client.close()
print('\nRestart tayyor. Endi monitor xabari kelsa "mos qurilma" topilishi kerak.')
