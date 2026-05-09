import os
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer


# =========================
# CẤU HÌNH
# =========================
input_path = "DACN1/feedback_labeled_balanced.csv"

tfidf_output_path = "DACN1/tfidf_vectorizer.pkl"
X_output_path = "DACN1/X_tfidf.pkl"
y_output_path = "DACN1/y_labels.pkl"

os.makedirs("DACN1", exist_ok=True)


# =========================
# ĐỌC DỮ LIỆU
# =========================
df = pd.read_csv(input_path, encoding="utf-8-sig")

# Ưu tiên dùng ml_text nếu có, vì đã tách từ bằng ViTokenizer
if "ml_text" in df.columns:
    text_column = "ml_text"
else:
    text_column = "clean_content"

label_column = "label"

if text_column not in df.columns:
    raise ValueError(f"Không tìm thấy cột văn bản: {text_column}")

if label_column not in df.columns:
    raise ValueError("Không tìm thấy cột label trong file CSV")


# Xóa dòng thiếu dữ liệu
df = df.dropna(subset=[text_column, label_column])

X_text = df[text_column].astype(str)
y = df[label_column].astype(str)


# =========================
# TF-IDF VECTORIZER
# =========================
tfidf = TfidfVectorizer(
    max_features=5000,       # lấy tối đa 5000 đặc trưng
    ngram_range=(1, 2),      # lấy từ đơn và cụm 2 từ
    min_df=2,                # từ phải xuất hiện ít nhất 2 văn bản
    max_df=0.9               # bỏ từ xuất hiện quá nhiều
)


# =========================
# CHUYỂN VĂN BẢN THÀNH VECTOR SỐ
# =========================
X_tfidf = tfidf.fit_transform(X_text)


# =========================
# LƯU KẾT QUẢ
# =========================
joblib.dump(tfidf, tfidf_output_path)
joblib.dump(X_tfidf, X_output_path)
joblib.dump(y, y_output_path)


print("Hoàn thành chuyển văn bản thành số bằng TF-IDF")
print("Cột văn bản sử dụng:", text_column)
print("Số mẫu:", X_tfidf.shape[0])
print("Số đặc trưng TF-IDF:", X_tfidf.shape[1])

print("Đã lưu TF-IDF vectorizer:", tfidf_output_path)
print("Đã lưu X_tfidf:", X_output_path)
print("Đã lưu y_labels:", y_output_path)