# app.py
import streamlit as st
import pandas as pd
import requests
import os

BASE_URL = "http://localhost:5000"
def get_all_users_api():
    try:
        response = requests.get(f"{BASE_URL}/api/get_users")
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal terhubung ke Backend: {e}")
        return pd.DataFrame() # Kembalikan DF kosong jika error
    
def get_all_jobs():
    try:
        res = requests.get(f"{BASE_URL}/api/get_jobs")
        res.raise_for_status()
        data = res.json()
        return pd.DataFrame(data)
        
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal terhubung ke Backend: {e}")
        return pd.DataFrame()
    
def upload_file_api(file, user_id):
    try:
        files = {'file': (file.name, file.getbuffer(), "application/pdf")}
        data = {'user_id': user_id}
        response = requests.post(f"{BASE_URL}/api/upload_cv", files=files, data=data)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengupload file: {e}")
        return None

def get_cv_file_path_by_user(user_id):
    try:
        response = requests.get(f"{BASE_URL}/api/cv_file_paths/{user_id}")
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal terhubung ke Backend: {e}")
        return pd.DataFrame()
    
def get_recommendation_api(user_id, cv_path):
    try:
        params = {"user_id": user_id, "cv_path": cv_path}
        response = requests.get(f"{BASE_URL}/api/recomendation", params=params)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mendapatkan rekomendasi: {e}")
        return pd.DataFrame()


# st.title("🔍 Sistem Rekomendasi Lowongan Kerja")

# ── Sidebar: Pilih User ─────────────────────────────────────
st.sidebar.header("👤 Menu Utama:")
menu = st.sidebar.radio("Pilih mode:", ["Analisis Feedback", "Rekomendasi Loker"], index=1)
st.sidebar.divider()


df_users  = get_all_users_api()
if not df_users.empty:
    user_dict = dict(zip(df_users["nama"], df_users["user_id"]))
    nama_user = st.sidebar.selectbox("Login sebagai:", list(user_dict.keys()))
    user_id   = user_dict[nama_user]
    st.sidebar.success(f"Login sebagai **{nama_user}** (ID: {user_id})")
else:
    st.sidebar.error("Database user kosong sepertinya")




if menu == "Analisis Feedback":
    
    tab1, tab2, tab3 = st.tabs(["📋 Daftar Lowongan", "❤️ Feedback Saya", "📊 Data Feedback"])
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
                    # simpan_feedback(user_id, row["job_id"], 1.0)
                    st.success("Tersimpan!")
                    st.rerun()

                if col_dislike.button("👎", key=f"dislike_{row['job_id']}"):
                    # simpan_feedback(user_id, row["job_id"], 0.0)
                    st.warning("Tersimpan!")
                    st.rerun()
            
            st.text(f"**Deskripsi:** {row['deskripsi']}...")  # Tampilkan potongan deskripsi

    with tab2:
        st.subheader(f"Feedback dari {nama_user}")
        # df_fb = get_feedback_user(user_id)

        # if df_fb.empty:
        #     st.info("Belum ada feedback. Berikan like/dislike di tab Daftar Lowongan!")
        # else:
        #     df_fb["feedback_label"] = df_fb["feedback_explicit"].map({1.0: "👍 Like", 0.0: "👎 Dislike"})
        #     st.dataframe(
        #         df_fb[["judul", "perusahaan", "skills", "feedback_label", "timestamp"]],
        #         width="stretch"
        #     )
        #     st.metric("Total Like", len(df_fb[df_fb["feedback_explicit"] == 1.0]))
        #     st.metric("Total Dislike", len(df_fb[df_fb["feedback_explicit"] == 0.0]))

    with tab3:
        st.subheader("📊 Semua Data Feedback (Data Training)")
        # df_all_fb = get_semua_feedback()

        # if df_all_fb.empty:
        #     st.info("Belum ada data feedback dari user manapun.")
        # else:
        #     st.dataframe(df_all_fb, width="stretch")
        #     st.metric("Total Interaksi", len(df_all_fb))
        #     st.metric("User Aktif", df_all_fb["user_id"].nunique())
        #     st.metric("Lowongan Dinilai", df_all_fb["job_id"].nunique())

        #     # Tombol export
        #     csv = df_all_fb.to_csv(index=False)
        #     st.download_button(
        #         "⬇️ Download Data Feedback (CSV)",
        #         data=csv,
        #         file_name="feedback_training.csv",
        #         mime="text/csv"
        #     )
        
        
        
        
        
else:
    st.header("🚧 Fitur Rekomendasi Lowongan Kerja")
    st.write("Upload CV dalam format .pdf yang anda miliki, untuk mencocokan dengan content loker paling relevan")
    col_upload, col_result = st.columns([1, 2])
    
    with col_upload:
        st.subheader("Pilih CV lama:")
        cv_history = get_cv_file_path_by_user(user_id)
        options = {os.path.basename(row["path"]): row["path"] for _, row in cv_history.iterrows()}
        
        selected_cv_name = st.selectbox(
            "Gunakan CV yang sudah ada:", 
            options=["-- Pilih CV --"] + list(options.keys())
        )
        if selected_cv_name != "-- Pilih CV --":
            st.success(f"CV '{selected_cv_name}' dipilih.")
        
        st.divider()
        
        st.subheader("Upload CV baru:")
        uploaded_file = st.file_uploader("Pilih file PDF CV anda", type=["pdf"])
        
        st.divider()
        
        btn_filter = st.button("Mulai filter lowongan", use_container_width=True)
    with col_result:
        st.subheader("Hasil Rekomendasi")
        if uploaded_file is not None and btn_filter:
            with st.spinner("Sedang mengekstrak teks dan menghitung kemiripan (BERT)..."):
                # Kirim ke Backend Flask
                df_data_up = upload_file_api(uploaded_file, user_id)
                file_path = df_data_up.get("path", "Tidak ada path")
                st.write(f"CV berhasil diupload ke path: {file_path}")
                df_rekomendasi = get_recommendation_api(user_id, file_path)
                
                # mulai proses rekomendasi
                
                
                # st.rerun()  # Refresh halaman untuk update CV history (opsional)
                
                if df_rekomendasi is not None:
                    st.success(f"Ditemukan {len(df_rekomendasi)} lowongan yang cocok!")
                    
                    for _, row in df_rekomendasi.iterrows():
                        with st.expander(f"✨ Score: {row.get('similarity_score', 0):.2f} | {row['judul']} - {row['perusahaan']}"):
                            st.write(f"📍 **Lokasi:** {row['provinsi']}")
                            st.write(f"💰 **Gaji:** Rp {row['gaji_min']:,.0f} - {row['gaji_max']:,.0f}")
                            st.write(f"🛠️ **Skills:** {row['skills']}")
                            st.divider()
                            # Gunakan cara replace \n yang kita bahas tadi agar rapi
                            desc = row['deskripsi'].replace("\n", "  \n")
                            st.markdown(f"**Deskripsi:** \n{desc}")
                            st.markdown(f"[🔗 Buka Link Lowongan]({row['link']})")
                else:
                    st.error("Gagal mendapatkan rekomendasi.")
                
                    
        elif selected_cv_name != "-- Pilih CV --" and btn_filter:
            with st.spinner("Sedang mengekstrak teks dan menghitung kemiripan (BERT)..."):
                selected_cv_path = options[selected_cv_name]
                # Kirim ke Backend Flask
                df_rekomendasi = get_recommendation_api(user_id, selected_cv_path)
                
                if df_rekomendasi is not None:
                    st.success(f"Ditemukan {len(df_rekomendasi)} lowongan yang cocok!")
                    
                    for _, row in df_rekomendasi.iterrows():
                        with st.expander(f"✨ Score: {row.get('similarity_score', 0):.2f} | {row['Judul']} - {row['Perusahaan']}"):
                            st.write(f"📍 **Lokasi:** {row['Provinsi']}")
                            st.write(f"💰 **Gaji:** Rp {row['Gaji_Min']:,.0f} - {row['Gaji_Max']:,.0f}")
                            st.write(f"🛠️ **Skills:** {row['Skills']}")
                            st.divider()
                            desc = row['Deskripsi'].replace("\n", "  \n")
                            st.markdown(f"**Deskripsi:** \n{desc}")
                            st.markdown(f"[🔗 Buka Link Lowongan]({row['Link']})")
                else:
                    st.error("Gagal mendapatkan rekomendasi.")
            
        else:
            st.info("Silakan upload CV dan tekan tombol 'Mulai Filter' untuk melihat hasil.")