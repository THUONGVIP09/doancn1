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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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