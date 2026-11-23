import sqlite3
from datetime import date
from logic import Quote

DB_PATH = "quotedesk.db"


def get_conn(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row            # access columns by name
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite ignores FKs unless you ask
    return conn


def init_db(path=DB_PATH):
    with get_conn(path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS rfqs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                part_number TEXT    NOT NULL,
                description TEXT    NOT NULL,
                quantity    INTEGER NOT NULL CHECK (quantity > 0),
                needed_by   TEXT    NOT NULL      -- ISO date: YYYY-MM-DD
            );
            CREATE TABLE IF NOT EXISTS quotes (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                rfq_id         INTEGER NOT NULL REFERENCES rfqs(id) ON DELETE CASCADE,
                supplier       TEXT    NOT NULL,
                unit_price_paise INTEGER NOT NULL CHECK (unit_price_paise >= 0),
                lead_time_days INTEGER NOT NULL CHECK (lead_time_days >= 0),
                valid_until    TEXT    NOT NULL   -- ISO date
            );
        """)


def create_rfq(part_number, description, quantity, needed_by: date, path=DB_PATH):
    with get_conn(path) as conn:
        cur = conn.execute(
            "INSERT INTO rfqs (part_number, description, quantity, needed_by) "
            "VALUES (?, ?, ?, ?)",
            (part_number, description, quantity, needed_by.isoformat()),
        )
        return cur.lastrowid


def add_quote(rfq_id, supplier, unit_price_rupees, lead_time_days,
              valid_until: date, path=DB_PATH):
    paise = round(unit_price_rupees * 100)    # store money as integer paise
    with get_conn(path) as conn:
        conn.execute(
            "INSERT INTO quotes (rfq_id, supplier, unit_price_paise, "
            "lead_time_days, valid_until) VALUES (?, ?, ?, ?, ?)",
            (rfq_id, supplier, paise, lead_time_days, valid_until.isoformat()),
        )


def get_rfq(rfq_id, path=DB_PATH):
    with get_conn(path) as conn:
        return conn.execute("SELECT * FROM rfqs WHERE id = ?", (rfq_id,)).fetchone()


def list_rfqs(path=DB_PATH):
    with get_conn(path) as conn:
        return conn.execute("SELECT * FROM rfqs ORDER BY needed_by").fetchall()


def get_quotes(rfq_id, path=DB_PATH):
    """Returns Quote objects (from logic.py), ready for best_quote()."""
    with get_conn(path) as conn:
        rows = conn.execute(
            "SELECT * FROM quotes WHERE rfq_id = ?", (rfq_id,)
        ).fetchall()
    return [
        Quote(
            supplier=r["supplier"],
            unit_price=r["unit_price_paise"] / 100,
            lead_time_days=r["lead_time_days"],
            valid_until=date.fromisoformat(r["valid_until"]),
        )
        for r in rows
    ]