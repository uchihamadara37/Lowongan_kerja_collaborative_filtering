# database.py
import sqlite3
import pandas as pd
from datetime import datetime
import uuid

# mencoba meniru java
from pydantic import BaseModel, Field
from typing import Optional
import uuid

DB_PATH = "loker_app.db"

# class
class User(BaseModel):
    user_id: str
    nama: str
    email: str
    
class Job(BaseModel):
    job_id: str
    judul: str
    industri: str
    tipe_pekerjaan: str
    kategori: str
    tanggal_post: str
    berlaku_hingga: str
    perusahaan: str
    kota: str
    provinsi: str
    negara: str
    gaji_min: Optional[float] = Field(default=0.0, ge=0.0)
    gaji_max: Optional[float] = Field(default=0.0, ge=0.0)
    gaji_currency: Optional[str]
    skills: Optional[str]
    pengalaman_bulan: Optional[float] = Field(default=0.0, ge=0.0)
    pendidikan: Optional[str]
    deskripsi: Optional[str]
    link: Optional[str]


def init_db():
    """Inisialisasi database dan tabel"""
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Tabel users (static)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id    TEXT PRIMARY KEY,
            nama       TEXT NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabel jobs (mirror dari CSV)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id          TEXT PRIMARY KEY,
            judul           TEXT,
            industri        TEXT,
            tipe_pekerjaan  TEXT,
            kategori        TEXT,
            tanggal_post    TEXT,
            berlaku_hingga  TEXT,
            perusahaan      TEXT,
            kota            TEXT,
            provinsi        TEXT,
            negara          TEXT,
            gaji_min            REAL,
            gaji_max            REAL,
            gaji_currency   TEXT,
            skills          TEXT,
            pengalaman_bulan    REAL,
            pendidikan      TEXT,
            deskripsi       TEXT,
            link            TEXT
        )
    """)

    # Tabel feedback
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id         TEXT PRIMARY KEY,
            user_id    INTEGER NOT NULL,
            job_id     INTEGER NOT NULL,
            feedback_explicit   REAL NOT NULL,  -- 1.0 = like, 0.0 = dislike
            feedback_implicit   REAL,            -- misal: waktu klik, frekuensi klik, dll (opsional)
            timestamp  TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (job_id)  REFERENCES jobs(job_id),
            UNIQUE(user_id, job_id)    -- 1 user hanya 1 feedback per lowongan
        )
    """)

    # Insert 5 user static (skip jika sudah ada)
    static_users = [
        (str(uuid.UUID("11111111-0000-0000-0000-000000000001")), "Andre",   "andre@email.com"),
        (str(uuid.UUID("11111111-0000-0000-0000-000000000002")), "Budi",    "budi@email.com"),
        (str(uuid.UUID("11111111-0000-0000-0000-000000000003")), "Citra",   "citra@email.com"),
        (str(uuid.UUID("11111111-0000-0000-0000-000000000004")), "Dewi",    "dewi@email.com"),
        (str(uuid.UUID("11111111-0000-0000-0000-000000000005")), "Eko",     "eko@email.com"),
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO users (user_id, nama, email)
        VALUES (?, ?, ?)
    """, static_users)

    conn.commit() 
    conn.close()  
    print("✅ Database siap!")


def import_jobs_dari_csv(csv_path: str):
    """Import data lowongan dari CSV ke tabel jobs"""
    df   = pd.read_csv(csv_path)
    conn = sqlite3.connect(DB_PATH)

    for _, row in df.iterrows():
        conn.execute("""
            INSERT OR IGNORE INTO jobs (
                job_id, 
                judul, 
                industri, 
                tipe_pekerjaan, 
                kategori, 
                tanggal_post,
                berlaku_hingga, 
                perusahaan, 
                kota, 
                provinsi, 
                negara,
                gaji_min, 
                gaji_max, 
                gaji_currency, 
                skills,
                pengalaman_bulan, 
                pendidikan, 
                deskripsi, 
                link
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),  # job_id unik
            row.get("Judul", ""),
            row.get("Industri", ""),
            row.get("Tipe", ""),
            row.get("Kategori", ""),
            row.get("Tanggal_Post", ""),
            row.get("Berlaku_Hingga", ""),
            row.get("Perusahaan", ""),
            row.get("Kota", ""),
            row.get("Provinsi", ""),
            row.get("Negara", ""),
            row.get("Gaji_Min", 0.0),
            row.get("Gaji_Max", 0.0),
            row.get("Gaji_Currency", ""),
            row.get("Skills", ""),
            row.get("Pengalaman_Bulan", 0.0),
            row.get("Pendidikan", ""),
            row.get("Deskripsi", ""),
            row.get("Link", "")
        ))

    conn.commit()
    conn.close()
    print(f"✅ {len(df)} lowongan diimport ke database!")


# ── Helper functions ────────────────────────────────────────

def get_all_users() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("SELECT * FROM users", conn)
    conn.close()
    return df

def get_all_jobs() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("SELECT * FROM jobs", conn)
    conn.close()
    return df

def get_feedback_user(user_id: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("""
        SELECT f.*, j.judul, j.perusahaan, j.skills
        FROM feedback f
        JOIN jobs j ON f.job_id = j.job_id
        WHERE f.user_id = ?
        ORDER BY f.timestamp DESC
    """, conn, params=(user_id,))
    conn.close()
    return df

def simpan_feedback(user_id: str, job_id: str, feedback: float):
    """Simpan atau update feedback user"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO feedback (user_id, job_id, feedback_explicit)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, job_id)
        DO UPDATE SET feedback_explicit = excluded.feedback_explicit,
                      timestamp = CURRENT_TIMESTAMP
    """, (user_id, job_id, feedback))
    conn.commit()
    conn.close()

def get_semua_feedback() -> pd.DataFrame:
    """Ambil semua feedback untuk keperluan training model"""
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("SELECT user_id, job_id, feedback_explicit FROM feedback", conn)
    conn.close()
    return df

init_db()
import_jobs_dari_csv("../glints_jobs_detail_clean.csv")