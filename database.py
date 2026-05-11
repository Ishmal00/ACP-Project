import sqlite3
from models import Member, Session

DB_NAME = "cyber_cafe.db"


def connect():
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            member_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            phone       TEXT NOT NULL,
            discount_percent REAL DEFAULT 30.0,
            join_date   TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            computer_no   INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            member_id     INTEGER,
            start_time    TEXT NOT NULL,
            end_time      TEXT,
            total_bill    REAL DEFAULT 0.0,
            is_active     INTEGER DEFAULT 1,
            FOREIGN KEY (member_id) REFERENCES members(member_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Tables created successfully!")



def add_member(member: Member):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO members (name, phone, discount_percent, join_date)
        VALUES (?, ?, ?, ?)
    ''', (member.name, member.phone, member.discount_percent, member.join_date))
    conn.commit()
    conn.close()
    print(f"Member '{member.name}' added!")


def get_all_members():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_member_by_id(member_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE member_id = ?", (member_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def delete_member(member_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE member_id = ?", (member_id,))
    conn.commit()
    conn.close()
    print(f"Member ID {member_id} deleted!")




def start_session(session: Session):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (computer_no, customer_name, member_id, start_time, is_active)
        VALUES (?, ?, ?, ?, 1)
    ''', (session.computer_no, session.customer_name, session.member_id, session.start_time))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"Session started! ID: {session_id}")
    return session_id


def end_session(session_id: int, end_time: str, total_bill: float):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE sessions
        SET end_time = ?, total_bill = ?, is_active = 0
        WHERE session_id = ?
    ''', (end_time, total_bill, session_id))
    conn.commit()
    conn.close()
    print(f"Session {session_id} ended. Bill: Rs. {total_bill:.2f}")


def get_active_sessions():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE is_active = 1")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_session_by_id(session_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_sessions():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions ORDER BY session_id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows




def get_daily_revenue(date: str):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(total_bill) FROM sessions
        WHERE DATE(start_time) = ? AND is_active = 0
    ''', (date,))
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else 0.0

if __name__ == "__main__":
    create_tables()
    print("Database initialized!")
