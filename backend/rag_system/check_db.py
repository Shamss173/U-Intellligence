import sqlite3

db_path = "metadata.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
try:
    cursor.execute("SELECT source_path FROM chunks WHERE source_file = 'DELETED' GROUP BY source_path")
    rows = cursor.fetchall()
    print("Soft-deleted files in chunks table:")
    for row in rows:
        print(dict(row))
except Exception as e:
    print("Error querying SQLite:", e)
conn.close()
