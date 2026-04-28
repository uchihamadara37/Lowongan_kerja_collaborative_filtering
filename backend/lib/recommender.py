from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import os

# Mengambil folder tempat script ini berada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMBEDD_LOKER_PATH = os.path.join(BASE_DIR, "..", "data_embedd_loker", "job_embeddings.npy")
DATA_MENTAH_CSV_PATH = os.path.join(BASE_DIR, "..", "..", "glints_jobs_detail_clean.csv")

# Load model sekali saja saat startup (Singleton pattern)
# model = SentenceTransformer('all-MiniLM-L6-v2')
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Load data CSV di awal
df_jobs = pd.read_csv(DATA_MENTAH_CSV_PATH)
job_embeddings = model.encode(df_jobs['teks_gabungan'].tolist(), convert_to_tensor=True, show_progress_bar=True)

np.save(EMBEDD_LOKER_PATH, job_embeddings)

def get_content_recommendations(user_cv_text, top_n=20):
    # Asumsikan df_jobs sudah memiliki kolom 'gabungan' yang kita buat sebelumnya
    cv_embedding = model.encode(user_cv_text, convert_to_tensor=True)
    
    # Hitung Cosine Similarity
    cosine_scores = util.cos_sim(cv_embedding, job_embeddings)[0]
    
    # Tambahkan skor ke dataframe
    df_jobs['similarity_score'] = cosine_scores.tolist()
    
    # Ambil top N
    return df_jobs.sort_values(by='similarity_score', ascending=False).head(top_n)