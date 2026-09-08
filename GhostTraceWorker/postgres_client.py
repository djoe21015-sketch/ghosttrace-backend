import psycopg2
from .config import POSTGRES

def pg_connect():
    return psycopg2.connect(
        host=POSTGRES["host"],
        port=POSTGRES["port"],
        user=POSTGRES["user"],
        password=POSTGRES["password"],
        database=POSTGRES["database"]
    )


def save_report_to_postgres(target: str, report_path: str, risk_score: dict):
    conn = pg_connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO reports (target, report_path, risk_score)
        VALUES (%s, %s, %s)
    """, (target, report_path, str(risk_score)))

    conn.commit()
    conn.close()
