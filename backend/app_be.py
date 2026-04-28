from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from lib.extractor import extract_text_from_pdf
from lib.recommender import get_content_recommendations
from database_be import get_all_jobs, get_all_users, get_feedback_user, simpan_feedback, get_semua_feedback, save_path_file, get_all_file_address, get_file_address_by_user
import pandas as pd

app = Flask(__name__)
CORS(app) # Penting agar Next.js bisa akses API ini tanpa masalah CORS

@app.route('/api/get_users', methods=['GET'])
def api_get_users():
    users = get_all_users()
    return jsonify(users.to_dict(orient="records"))

@app.route('/api/get_jobs', methods=['GET'])
def api_get_jobs():
    jobs = get_all_jobs()
    return jsonify(jobs.to_dict(orient="records"))

@app.route('/api/get_feedback/<string:user_id>', methods=['GET'])
def api_get_feedback(user_id):
    feedback = get_feedback_user(user_id)
    return jsonify(feedback.to_dict(orient="records"))

@app.route('/api/upload_cv/', methods=['POST'])
def upload_cv():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    user_id = request.form.get("user_id")
    
    path = os.path.join("uploads", file.filename)
    if not file.filename in os.listdir("uploads") and not user_id is None:    
        # Simpan sementara
        file.save(path)
        
    if user_id is not None :
        # Simpan path file ke databa
        save_path_file(path, user_id)
    
    
    cv_text = extract_text_from_pdf(path)
    print(cv_text[:50])
    
    # 2. Jalankan Content Filtering (BERT)
    # recommendations = get_content_recommendations(cv_text, top_n=20)
    
    # 3. Kembalikan hasil sebagai JSON
    # return jsonify(recommendations.to_dict(orient="records"))
    return jsonify({"message": "CV diterima, tapi rekomendasi belum diimplementasikan", "path": path})

@app.route('/api/cv_file_paths', methods=['GET'])
def get_cv_file_paths():
    # Endpoint untuk mendapatkan semua path file CV yang sudah diupload
    df = get_all_file_address()
    return jsonify(df.to_dict(orient="records"))

@app.route('/api/cv_file_paths/<string:user_id>', methods=['GET'])
def get_cv_file_paths_by_user(user_id):
    # Endpoint untuk mendapatkan path file CV berdasarkan user_id
    df = get_file_address_by_user(user_id)
    return jsonify(df.to_dict(orient="records"))


@app.route('/api/recomendation', methods=['GET'])
def get_recomendation():
    if 'user_id' not in request.args:
        return jsonify({"error": "Missing user_id parameter"}), 400
    if 'cv_path' not in request.args:
        return jsonify({"error": "Missing cv_path parameter"}), 400
    
    # sebenarnya harus dicocokan antara user_id dan cv_path, tapi untuk sementara kita asumsikan sudah benar saja
    
    cv_text = extract_text_from_pdf(request.args.get("cv_path"))
    recommendations = get_content_recommendations(cv_text, top_n=20)
    
    # Endpoint untuk get_all_jobs biasa
    # return jsonify(df_jobs.head(50).to_dict(orient="records"))
    return jsonify(recommendations.to_dict(orient="records"))

if __name__ == '__main__':
    app.run(debug=True, port=5000)