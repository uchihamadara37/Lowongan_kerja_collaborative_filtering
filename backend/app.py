from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from lib.extractor import extract_text_from_pdf
from lib.recommender import get_content_recommendations
from database import get_all_jobs, get_all_users, get_feedback_user, save_feedback, get_semua_feedback
import pandas as pd

app = Flask(__name__)
CORS(app) # Penting agar Next.js bisa akses API ini tanpa masalah CORS

@app.route('api/get_users', methods=['GET'])
def api_get_users():
    users = get_all_users()
    return jsonify(users.to_dict(orient="records"))

@app.route('/api/get_jobs', methods=['GET'])
def api_get_jobs():
    jobs = get_all_jobs()
    return jsonify(jobs.to_dict(orient="records"))

@app.route('/api/get_feedback/<str:user_id>', methods=['GET'])
def api_get_feedback(user_id):
    feedback = get_feedback_user(user_id)
    return jsonify(feedback.to_dict(orient="records"))

@app.route('/api/upload_cv', methods=['POST'])
def upload_cv():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    user_id = request.form.get("user_id")
    
    # Simpan sementara
    path = os.path.join("uploads", file.filename)
    file.save(path)
    
    # 1. Ekstrak Teks
    cv_text = extract_text_from_pdf(path)
    
    # 2. Jalankan Content Filtering (BERT)
    recommendations = get_content_recommendations(cv_text, top_n=20)
    
    # 3. Kembalikan hasil sebagai JSON
    return jsonify(recommendations.to_dict(orient="records"))

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    # Endpoint untuk get_all_jobs biasa
    # return jsonify(df_jobs.head(50).to_dict(orient="records"))
    return jsonify("endpoint belum diimplementasikan")



if __name__ == '__main__':
    app.run(debug=True, port=5000)