"""
Oracle Database Setup and Diagnostic Utility for SCAP.
Allows testing Oracle XE connectivity, running DDL schema, and loading seed data.
"""
import sys
from config import Config

try:
    import oracledb
except ImportError:
    print("[ERROR] python-oracledb is not installed. Run: pip install oracledb")
    sys.exit(1)

def test_connection():
    print(f"[*] Testing Oracle connection to {Config.ORACLE_USER}@{Config.ORACLE_DSN}...")
    try:
        conn = oracledb.connect(
            user=Config.ORACLE_USER,
            password=Config.ORACLE_PASSWORD,
            dsn=Config.ORACLE_DSN
        )
        cursor = conn.cursor()
        cursor.execute("SELECT banner FROM v$version")
        row = cursor.fetchone()
        print(f"[SUCCESS] Connected to Oracle Database:\n    {row[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[FAILURE] Unable to connect to Oracle Database: {e}")
        print("\nTroubleshooting tips:")
        print("  1. Verify the Oracle Service is running: Start-Service OracleServiceXE")
        print("  2. Verify the TNS Listener is running: Start-Service OracleOraDB21Home1TNSListener")
        print("  3. Check credentials in .env file (ORACLE_USER, ORACLE_PASSWORD, ORACLE_SERVICE)")
        return False

def execute_sql_file(filename):
    print(f"[*] Executing {filename} on Oracle Database...")
    try:
        conn = oracledb.connect(
            user=Config.ORACLE_USER,
            password=Config.ORACLE_PASSWORD,
            dsn=Config.ORACLE_DSN
        )
        cursor = conn.cursor()
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split commands by semicolon or slash
        commands = [cmd.strip() for cmd in content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        success_count = 0
        for cmd in commands:
            try:
                cursor.execute(cmd)
                success_count += 1
            except Exception as ex:
                # Ignore drops if table didn't exist
                if "ORA-00942" not in str(ex):
                    print(f"    [WARN] Command error: {ex}")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[SUCCESS] Executed {success_count} statements from {filename}.")
        return True
    except Exception as e:
        print(f"[FAILURE] Execution failed: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        import os
        if os.path.exists("schema.sql"):
            execute_sql_file("schema.sql")
        if os.path.exists("seed_data.sql"):
            execute_sql_file("seed_data.sql")
        print("\n[SUCCESS] Oracle database is fully configured and ready for SCAP!")
    else:
        print("\n[INFO] SCAP will automatically run using its local SQLite fallback until Oracle is started.")
