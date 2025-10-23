
import sqlite3
from sqlite3 import Connection
import pandas as pd
from datetime import datetime

DB_PATH = "client_app.db"

def get_conn() -> Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sex TEXT,
            age INTEGER,
            height_cm REAL,
            weight_kg REAL,
            skinfolds TEXT,
            body_fat_pct REAL,
            muscle_pct REAL,
            visceral_fat INTEGER,
            preferred_foods TEXT,
            meals_per_day INTEGER,
            allergies TEXT,
            economic_level TEXT,
            occupation TEXT,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            weight_kg REAL,
            body_fat_pct REAL,
            muscle_pct REAL,
            visceral_fat INTEGER,
            waist_cm REAL,
            hip_cm REAL,
            chest_cm REAL,
            thigh_cm REAL,
            arm_cm REAL,
            notes TEXT,
            FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS meal_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            calories INTEGER,
            protein_g REAL,
            fats_g REAL,
            carbs_g REAL,
            meals_json TEXT,
            notes TEXT,
            FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS training_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            goal TEXT,
            split TEXT,
            days_per_week INTEGER,
            session_duration_min INTEGER,
            cardio_plan TEXT,
            routine_text TEXT,
            notes TEXT,
            FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def create_client(**kwargs) -> int:
    conn = get_conn()
    cur = conn.cursor()
    fields = [
        "name","sex","age","height_cm","weight_kg","skinfolds","body_fat_pct",
        "muscle_pct","visceral_fat","preferred_foods","meals_per_day","allergies",
        "economic_level","occupation","notes","created_at"
    ]
    values = [kwargs.get(f) for f in fields]
    cur.execute(
        f"INSERT INTO clients ({', '.join(fields)}) VALUES ({', '.join(['?']*len(fields))})",
        values,
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def update_client(client_id: int, **kwargs):
    conn = get_conn()
    cur = conn.cursor()
    allowed = [
        "name","sex","age","height_cm","weight_kg","skinfolds","body_fat_pct",
        "muscle_pct","visceral_fat","preferred_foods","meals_per_day","allergies",
        "economic_level","occupation","notes"
    ]
    sets, vals = [], []
    for k in allowed:
        if k in kwargs:
            sets.append(f"{k} = ?")
            vals.append(kwargs[k])
    vals.append(client_id)
    if sets:
        cur.execute(f"UPDATE clients SET {', '.join(sets)} WHERE id = ?", vals)
        conn.commit()
    conn.close()

def delete_client(client_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()

def list_clients(search=None) -> pd.DataFrame:
    conn = get_conn()
    query = "SELECT * FROM clients ORDER BY created_at DESC"
    params = []
    if search:
        query = ("SELECT * FROM clients WHERE name LIKE ? OR occupation LIKE ? OR notes LIKE ? "
                 "ORDER BY created_at DESC")
        like = f"%{search}%"
        params = [like, like, like]
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_client_by_id(client_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    row = cur.fetchone()
    conn.close()
    return row

def add_measurement(**kwargs):
    conn = get_conn()
    cur = conn.cursor()
    fields = [
        "client_id","date","weight_kg","body_fat_pct","muscle_pct","visceral_fat",
        "waist_cm","hip_cm","chest_cm","thigh_cm","arm_cm","notes"
    ]
    values = [kwargs.get(f) for f in fields]
    cur.execute(
        f"INSERT INTO measurements ({', '.join(fields)}) VALUES ({', '.join(['?']*len(fields))})",
        values,
    )
    conn.commit()
    conn.close()

def get_measurements(client_id: int) -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM measurements WHERE client_id = ? ORDER BY date DESC",
        conn,
        params=(client_id,),
    )
    conn.close()
    return df

def add_meal_plan(**kwargs):
    conn = get_conn()
    cur = conn.cursor()
    fields = [
        "client_id","date","calories","protein_g","fats_g","carbs_g","meals_json","notes"
    ]
    values = [kwargs.get(f) for f in fields]
    cur.execute(
        f"INSERT INTO meal_plans ({', '.join(fields)}) VALUES ({', '.join(['?']*len(fields))})",
        values,
    )
    conn.commit()
    conn.close()

def list_meal_plans(client_id: int) -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT id, date, calories, protein_g, fats_g, carbs_g, notes FROM meal_plans WHERE client_id = ? ORDER BY date DESC",
        conn,
        params=(client_id,),
    )
    conn.close()
    return df

def add_training_plan(**kwargs):
    conn = get_conn()
    cur = conn.cursor()
    fields = [
        "client_id","date","goal","split","days_per_week","session_duration_min","cardio_plan","routine_text","notes"
    ]
    values = [kwargs.get(f) for f in fields]
    cur.execute(
        f"INSERT INTO training_plans ({', '.join(fields)}) VALUES ({', '.join(['?']*len(fields))})",
        values,
    )
    conn.commit()
    conn.close()

def list_training_plans(client_id: int) -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT id, date, goal, split, days_per_week, session_duration_min FROM training_plans WHERE client_id = ? ORDER BY date DESC",
        conn,
        params=(client_id,),
    )
    conn.close()
    return df
