import paramiko

def get_tables():
    host = "192.168.1.150"
    user = "nishan"
    password = "6WKW5_3w2w5121"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    sftp = ssh.open_sftp()
    
    script = """
import sqlite3

db_path = "/home/nishan/flask_replica/the_bench.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
print("--- Tables in DB ---")
for t in tables:
    print(t[0])

# Also print columns for 'case' if found
try:
    # Try multiple case variations just in case
    cur.execute("PRAGMA table_info('case');")
    cols = cur.fetchall()
    print("--- Columns in 'case' ---")
    for c in cols:
         print(f"{c[1]} ({c[2]})")
except Exception as e:
    print(f"Error reading 'case' columns: {e}")

conn.close()
"""
    with sftp.open("/home/nishan/info_db.py", "w") as f:
        f.write(script)
    sftp.close()

    stdin, stdout, stderr = ssh.exec_command("python3 /home/nishan/info_db.py")
    out = stdout.read().decode('utf-8')
    print(out)

    ssh.close()

if __name__ == "__main__":
    get_tables()
