"""
Port 6006 ga kelayotgan barcha raw TCP ma'lumotni ko'rish.
30 soniya tinglaydi va birinchi kelgan xabarni chiqaradi.
"""
import sys, time
try:
    import paramiko
except ImportError:
    print("pip install paramiko"); sys.exit(1)

PASSWORD = "Ziyrak2025Ai"
HOST = "167.71.53.238"
USER = "root"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Ulanish: {USER}@{HOST}")
client.connect(HOST, username=USER, password=PASSWORD, timeout=30)

def run(cmd, label='', timeout=60):
    if label:
        print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors='replace').strip()
    if out:
        print(out[:3000].encode('ascii', errors='replace').decode())
    return out

# tcpdump bilan port 6006 ga kelgan paketlarni ko'rish (30 soniya)
print("\n30 soniya port 6006 ga kelgan TCP ma'lumotni ko'rish...")
print("(monitor yuborayotgan barcha raw ma'lumot ko'rinadi)\n")

run(
    "timeout 30 tcpdump -i any -A -s 2048 'tcp port 6006 and not src host 127.0.0.1' 2>&1 | head -100",
    "TCP dump port 6006 (30s)",
    timeout=35
)

client.close()
