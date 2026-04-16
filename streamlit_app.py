# app.py
import streamlit as st
import pandas as pd
from database import (
    init_db, import_jobs_dari_csv,
    get_all_users, get_all_jobs,
    get_feedback_user, simpan_feedback,
    get_semua_feedback
)

# ── Inisialisasi ────────────────────────────────────────────
init_db()
# import_jobs_dari_csv("glints_jobs_detail_clean.csv")

# st.set_page_config(page_title="Rekomendasi Loker", layout="wide")
st.title("🔍 Sistem Rekomendasi Lowongan Kerja")

# ── Sidebar: Pilih User ─────────────────────────────────────
st.sidebar.header("👤 Pilih User")
df_users  = get_all_users()
user_dict = dict(zip(df_users["nama"], df_users["user_id"]))
nama_user = st.sidebar.selectbox("Login sebagai:", list(user_dict.keys()))
user_id   = user_dict[nama_user]
st.sidebar.success(f"Login sebagai **{nama_user}** (ID: {user_id})")

# ── Tab Navigasi ────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 Daftar Lowongan", "❤️ Feedback Saya", "📊 Data Feedback"])

# ─── TAB 1: Daftar Lowongan + Tombol Feedback ───────────────
with tab1:
    st.subheader("Semua Lowongan Tersedia")
    df_jobs = get_all_jobs()

    # Filter pencarian 
    search = st.text_input("🔎 Cari lowongan...", placeholder="Data Analyst, Python, Jakarta")
    if search:
        mask    = df_jobs.apply(lambda row: search.lower() in row.to_string().lower(), axis=1)
        df_jobs = df_jobs[mask]

    st.caption(f"Menampilkan {len(df_jobs)} lowongan")

    # Tampilkan per card
    for _, row in df_jobs.iterrows():
        st.divider()
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"**{row['judul']}** — {row['perusahaan']} | 📍 {row['provinsi']}")
            st.write(f"💰 **Gaji:** Rp {row['gaji_min']:,.0f} – {row['gaji_max']:,.0f}")
            st.write(f"🛠️ **Skills:** {row['skills']}")
            st.write(f"📅 **Tanggal Post:** {row['tanggal_post']} | **Berlaku Hingga:** {row['berlaku_hingga']}")
            st.markdown(f"[🔗 Lihat Lowongan]({row['link']})")

        with col2:
            st.write("**Feedback kamu:**")
            col_like, col_dislike = st.columns(2)

            if col_like.button("👍", key=f"like_{row['job_id']}"):
                simpan_feedback(user_id, row["job_id"], 1.0)
                st.success("Tersimpan!")
                st.rerun()

            if col_dislike.button("👎", key=f"dislike_{row['job_id']}"):
                simpan_feedback(user_id, row["job_id"], 0.0)
                st.warning("Tersimpan!")
                st.rerun()
        
        st.text(f"**Deskripsi:** {row['deskripsi']}...")  # Tampilkan potongan deskripsi

# ─── TAB 2: Riwayat Feedback User ───────────────────────────
with tab2:
    st.subheader(f"Feedback dari {nama_user}")
    df_fb = get_feedback_user(user_id)

    if df_fb.empty:
        st.info("Belum ada feedback. Berikan like/dislike di tab Daftar Lowongan!")
    else:
        df_fb["feedback_label"] = df_fb["feedback_explicit"].map({1.0: "👍 Like", 0.0: "👎 Dislike"})
        st.dataframe(
            df_fb[["judul", "perusahaan", "skills", "feedback_label", "timestamp"]],
            width="stretch"
        )
        st.metric("Total Like", len(df_fb[df_fb["feedback_explicit"] == 1.0]))
        st.metric("Total Dislike", len(df_fb[df_fb["feedback_explicit"] == 0.0]))

# ─── TAB 3: Semua Data Feedback (untuk training) ────────────
with tab3:
    st.subheader("📊 Semua Data Feedback (Data Training)")
    df_all_fb = get_semua_feedback()

    if df_all_fb.empty:
        st.info("Belum ada data feedback dari user manapun.")
    else:
        st.dataframe(df_all_fb, width="stretch")
        st.metric("Total Interaksi", len(df_all_fb))
        st.metric("User Aktif", df_all_fb["user_id"].nunique())
        st.metric("Lowongan Dinilai", df_all_fb["job_id"].nunique())

        # Tombol export
        csv = df_all_fb.to_csv(index=False)
        st.download_button(
            "⬇️ Download Data Feedback (CSV)",
            data=csv,
            file_name="feedback_training.csv",
            mime="text/csv"
        )