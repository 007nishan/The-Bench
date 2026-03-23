import paramiko

def migrate():
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

def add_column(table, col, stmt):
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {stmt}")
        print(f"Added column {col} to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"Column {col} already exists in {table}")
        else:
            print(f"Error adding {col}: {e}")

# Apply necessary migrations for Case
add_column("case", "case_type", "VARCHAR(20) DEFAULT 'standard'")
add_column("case", "description", "TEXT")
add_column("case", "public_filer_name", "VARCHAR(100)")
add_column("case", "public_filer_contact", "VARCHAR(100)")

conn.commit()
conn.close()
print("Migration completed.")
"""
    # Write safe migration script
    with sftp.open("/home/nishan/fix_db.py", "w") as f:
        f.write(script)
    sftp.close()

    stdin, stdout, stderr = ssh.exec_command("python3 /home/nishan/fix_db.py")
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')

    print("--- DB Migration Output ---")
    print(out)
    if err:
        print("--- Errors ---")
        print(err)

    ssh.close()

if __name__ == "__main__":
    migrate()
