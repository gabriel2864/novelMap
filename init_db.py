import sqlite3
from pathlib import Path

def init_db(db_path: str = "novelzone.db", schema_path: str = "schema.sql") -> None:
    """ Initialize the SQLite database from the schema.sql file """

    root = Path(__file__).resolve().parent
    db_file = root / db_path
    schema_file = root / schema_path

    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    
    conn = sqlite3.connect(db_file)
    try:
        with schema_file.open("r", encoding="utf-8") as f:
            sql_script = f.read()

        conn.executescript(sql_script)
        conn.commit()
        print(f"Database initialized at: {db_file}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
