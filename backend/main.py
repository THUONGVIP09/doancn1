from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import shutil
import os
import mysql.connector
from fastapi.staticfiles import StaticFiles
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import joblib
from pydantic import BaseModel

import requests
class ClassifyRequest(BaseModel):
    content: str
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class VerifyLocationRequest(BaseModel):
    query: str


VIETMAP_SERVICES_KEY = "ed9c43c7c34836b71f11afe43e42e6103b1b2bf886421643"

UPLOAD_FOLDER = r"D:\HK6\doancn1_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")


DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "dacn1_db"
}
MODEL_PATH = r"../DACN1/model_outputs/models/cnn_model.keras"
TOKENIZER_PATH = r"../DACN1/model_outputs/models/tokenizer.pkl"
LABEL_ENCODER_PATH = r"../DACN1/model_outputs/models/label_encoder.pkl"

cnn_model = load_model(MODEL_PATH)
CLASS_DISPLAY_NAMES = {
    "duong_cau_ha_tang_hu_hong": "Đường, cầu, hạ tầng hư hỏng",
    "dien_luc_chieu_sang": "Điện lực, chiếu sáng",
    "cong_ho_ga_thoat_nuoc": "Cống, hố ga, thoát nước",
    "via_he_long_duong": "Vỉa hè, lòng đường",
    "cay_xanh_vat_can": "Cây xanh, vật cản",
    "bien_bao": "Biển báo",
    "to_chuc_giao_thong": "Tổ chức giao thông",
    "den_tin_hieu": "Đèn tín hiệu",
    "rac_thai_ve_sinh_moi_truong": "Rác thải, vệ sinh môi trường",
    "do_xe_can_tro": "Đỗ xe cản trở",
    "khac": "Khác"
}

with open(TOKENIZER_PATH, "rb") as f:
    tokenizer = pickle.load(f)

label_encoder = joblib.load(LABEL_ENCODER_PATH)

MAX_LEN = cnn_model.input_shape[1]

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.get("/")
def home():
    return {
        "message": "Backend FastAPI đã kết nối MySQL"
    }

def predict_text_class(title, content):
    text = f"{title} {content}"

    sequence = tokenizer.texts_to_sequences([text])

    padded = pad_sequences(
        sequence,
        maxlen=MAX_LEN,
        padding="post",
        truncating="post"
    )

    predictions = cnn_model.predict(padded)

    predicted_index = int(np.argmax(predictions[0]))
    confidence = float(np.max(predictions[0]))

    predicted_category = label_encoder.inverse_transform([predicted_index])[0]
    predicted_name = CLASS_DISPLAY_NAMES.get(predicted_category, predicted_category)

    return predicted_category, predicted_name, confidence
@app.post("/predict")
async def predict_report(
    title: str = Form(...),
    content: str = Form(...),
    location: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    image_path = None

    if image:
        image_save_path = os.path.join(UPLOAD_FOLDER, image.filename)

        with open(image_save_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_path = f"/uploads/{image.filename}"

    text = f"{title} {content}".lower()

    predicted_category = "khac"
    predicted_name = "Khác"

    predicted_category, predicted_name, confidence = predict_text_class(title, content)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        INSERT INTO reports
        (title, content, location, image_path, predicted_category, predicted_name, status, confidence)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        title,
        content,
        location,
        image_path,
        predicted_category,
        predicted_name,
        "Chờ xử lý",
        confidence
    )

    cursor.execute(sql, values)
    conn.commit()

    new_id = cursor.lastrowid

    cursor.execute("SELECT * FROM reports WHERE id = %s", (new_id,))
    new_report = cursor.fetchone()
    new_report["confidence"] = confidence

    cursor.close()
    conn.close()

    return new_report


@app.get("/reports")
def get_all_reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
    reports = cursor.fetchall()

    cursor.close()
    conn.close()

    return reports


@app.get("/reports/{category}")
def get_reports_by_category(category: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT * FROM reports
        WHERE predicted_category = %s
        ORDER BY created_at DESC
    """

    cursor.execute(sql, (category,))
    reports = cursor.fetchall()

    cursor.close()
    conn.close()

    return reports


@app.get("/report/{report_id}")
def get_report_detail(report_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
    report = cursor.fetchone()

    cursor.close()
    conn.close()

    if not report:
        return {
            "error": "Không tìm thấy phản ánh"
        }

    return report
@app.post("/classify-text")
def classify_text_api(request: ClassifyRequest):
    content = request.content

    predicted_category, predicted_name, confidence = predict_text_class("", content)

    return {
        "predicted_category": predicted_category,
        "predicted_name": predicted_name,
        "confidence": confidence
    }
@app.post("/upload-chat-image")
async def upload_chat_image(image: UploadFile = File(...)):
    image_save_path = os.path.join(UPLOAD_FOLDER, image.filename)

    with open(image_save_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_path = f"/uploads/{image.filename}"

    return {
        "image_path": image_path
    }
    
    
@app.post("/verify-location")
def verify_location(request: VerifyLocationRequest):
    query = request.query.strip()
    

    if not query or len(query) < 5:
        return {
            "valid": False,
            "address": None,
            "lat": None,
            "lng": None
        }
    DEFAULT_PROVINCE = "tỉnh Vĩnh Long"
    query_original = query

    if "vĩnh long" not in query.lower() and "vinh long" not in query.lower():
        query = f"{query}, {DEFAULT_PROVINCE}"

    url = "https://maps.vietmap.vn/api/search/v3"

    try:
        response = requests.get(
            url,
            params={
                "apikey": VIETMAP_SERVICES_KEY,
                "text": query
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        print("Vietmap search result:", data)

        if not data:
            return {
                "valid": False,
                "address": None,
                "lat": None,
                "lng": None
            }

        results = data if isinstance(data, list) else [data]

        for item in results[:5]:
            address = (
                item.get("display")
                or item.get("address")
                or item.get("name")
            )

            lat = item.get("lat")
            lng = item.get("lng")

            if not address:
                continue

            address_lower = address.lower()

            # Chỉ nhận kết quả thuộc tỉnh Vĩnh Long
            if "vĩnh long" not in address_lower and "vinh long" not in address_lower:
                continue

            # Kiểm tra địa điểm gốc hoặc địa điểm đã nối Vĩnh Long có khớp kết quả không
            if is_location_match(query_original, address) or is_location_match(query, address):
                return {
                    "valid": True,
                    "address": address,
                    "lat": lat,
                    "lng": lng
                }

        # Nếu không có kết quả nào phù hợp
        return {
            "valid": False,
            "address": None,
            "lat": None,
            "lng": None
        }

    except Exception as e:
        print("Verify location error:", e)

        return {
            "valid": False,
            "address": None,
            "lat": None,
            "lng": None
        }
import unicodedata
import re
from difflib import SequenceMatcher


def remove_vietnamese_accents(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFD", text)
    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )
    text = text.replace("đ", "d").replace("Đ", "D")
    return text


def normalize_location_text(text: str) -> str:
    text = remove_vietnamese_accents(text.lower())
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def location_similarity(query: str, result_address: str) -> float:
    query_norm = normalize_location_text(query)
    result_norm = normalize_location_text(result_address)

    if not query_norm or not result_norm:
        return 0.0

    return SequenceMatcher(None, query_norm, result_norm).ratio()


def token_overlap_score(query: str, result_address: str) -> float:
    query_norm = normalize_location_text(query)
    result_norm = normalize_location_text(result_address)

    stopwords = {
        "duong", "doan", "tu", "den", "tai", "o", "gan",
        "phuong", "xa", "quan", "huyen", "tinh", "thanh", "pho",
        "cho", "khu", "vuc"
    }

    query_tokens = {
        token for token in query_norm.split()
        if len(token) >= 3 and token not in stopwords
    }

    result_tokens = {
        token for token in result_norm.split()
        if len(token) >= 3 and token not in stopwords
    }

    if not query_tokens:
        return 0.0

    overlap = query_tokens.intersection(result_tokens)
    return len(overlap) / len(query_tokens)


def is_location_match(query: str, result_address: str) -> bool:
    seq_score = location_similarity(query, result_address)
    overlap_score = token_overlap_score(query, result_address)

    print("VERIFY QUERY:", query)
    print("VERIFY RESULT:", result_address)
    print("SEQ SCORE:", seq_score)
    print("OVERLAP SCORE:", overlap_score)

    # Điều kiện chấp nhận:
    # - Chuỗi khá giống nhau
    # - Hoặc có nhiều từ khóa địa danh trùng nhau
    if seq_score >= 0.45:
        return True

    if overlap_score >= 0.5:
        return True

    return False