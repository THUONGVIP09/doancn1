import os
import joblib
import pandas as pd
import numpy as np

from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences


# =========================
# CẤU HÌNH
# =========================
output_dir = "DACN1/model_outputs"
model_dir = f"{output_dir}/models"
split_dir = f"{output_dir}/splits"
result_dir = f"{output_dir}/results"

test_path = f"{split_dir}/test_set.csv"

TEXT_COLUMN = "ml_text"
LABEL_ENCODED_COLUMN = "label_encoded"

MAX_LEN = 120

os.makedirs(result_dir, exist_ok=True)


# =========================
# LOAD TEST SET
# =========================
test_df = pd.read_csv(test_path, encoding="utf-8-sig")

X_test = test_df[TEXT_COLUMN].astype(str)
y_test = test_df[LABEL_ENCODED_COLUMN].values

label_encoder = joblib.load(f"{model_dir}/label_encoder.pkl")
target_names = label_encoder.classes_

print("Số mẫu test:", len(test_df))
print("\nPhân bố label trong test:")
print(test_df["label"].value_counts())


# =========================
# HÀM ĐÁNH GIÁ
# =========================
results = []

def evaluate_model(model_name, y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro")
    weighted_f1 = f1_score(y_true, y_pred, average="weighted")

    results.append({
        "model": model_name,
        "accuracy": acc,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1
    })

    print("\n" + "=" * 100)
    print("MÔ HÌNH:", model_name)
    print("=" * 100)
    print("Accuracy:", acc)
    print("Macro F1:", macro_f1)
    print("Weighted F1:", weighted_f1)

    report = classification_report(
        y_true,
        y_pred,
        target_names=target_names,
        output_dict=True,
        zero_division=0
    )

    report_df = pd.DataFrame(report).transpose()
    report_df.to_csv(
        f"{result_dir}/classification_report_{model_name}.csv",
        encoding="utf-8-sig"
    )

    cm = confusion_matrix(y_true, y_pred)
    cm_df = pd.DataFrame(
        cm,
        index=target_names,
        columns=target_names
    )
    cm_df.to_csv(
        f"{result_dir}/confusion_matrix_{model_name}.csv",
        encoding="utf-8-sig"
    )

    print("\nClassification report:")
    print(classification_report(
        y_true,
        y_pred,
        target_names=target_names,
        zero_division=0
    ))

    print("\nConfusion matrix:")
    print(cm_df)


# ============================================================
# 1. ĐÁNH GIÁ NAIVE BAYES
# ============================================================
nb_model = joblib.load(f"{model_dir}/naive_bayes_tfidf.pkl")
nb_pred = nb_model.predict(X_test)

evaluate_model("naive_bayes", y_test, nb_pred)


# ============================================================
# 2. ĐÁNH GIÁ SVM
# ============================================================
svm_model = joblib.load(f"{model_dir}/svm_tfidf.pkl")
svm_pred = svm_model.predict(X_test)

evaluate_model("svm", y_test, svm_pred)


# ============================================================
# CHUẨN BỊ DỮ LIỆU TEST CHO CNN / LSTM
# ============================================================
tokenizer = joblib.load(f"{model_dir}/tokenizer.pkl")

X_test_seq = tokenizer.texts_to_sequences(X_test)

X_test_pad = pad_sequences(
    X_test_seq,
    maxlen=MAX_LEN,
    padding="post",
    truncating="post"
)


# ============================================================
# 3. ĐÁNH GIÁ CNN
# ============================================================
cnn_model = tf.keras.models.load_model(f"{model_dir}/cnn_model.keras")

cnn_prob = cnn_model.predict(X_test_pad)
cnn_pred = np.argmax(cnn_prob, axis=1)

evaluate_model("cnn", y_test, cnn_pred)


# ============================================================
# 4. ĐÁNH GIÁ LSTM
# ============================================================
lstm_model = tf.keras.models.load_model(f"{model_dir}/lstm_model.keras")

lstm_prob = lstm_model.predict(X_test_pad)
lstm_pred = np.argmax(lstm_prob, axis=1)

evaluate_model("lstm", y_test, lstm_pred)


# =========================
# LƯU BẢNG SO SÁNH
# =========================
result_df = pd.DataFrame(results)

result_path = f"{result_dir}/model_comparison_results.csv"
result_df.to_csv(result_path, index=False, encoding="utf-8-sig")

print("\n" + "=" * 100)
print("BẢNG SO SÁNH 4 MÔ HÌNH")
print("=" * 100)
print(result_df)

print("\nĐã lưu kết quả tại:", result_path)
print("Đã lưu classification report và confusion matrix tại:", result_dir)