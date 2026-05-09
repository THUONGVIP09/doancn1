import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
import tensorflow as tf

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout, LSTM
from tensorflow.keras.callbacks import EarlyStopping


# =========================
# CẤU HÌNH
# =========================
input_path = "DACN1/feedback_labeled_balanced.csv"

output_dir = "DACN1/model_outputs"
model_dir = f"{output_dir}/models"
split_dir = f"{output_dir}/splits"

TEXT_COLUMN = "ml_text"
LABEL_COLUMN = "label"

TEST_SIZE = 0.2
RANDOM_STATE = 42

MAX_WORDS = 10000
MAX_LEN = 120
EMBEDDING_DIM = 128

os.makedirs(model_dir, exist_ok=True)
os.makedirs(split_dir, exist_ok=True)


# =========================
# ĐỌC DỮ LIỆU
# =========================
df = pd.read_csv(input_path, encoding="utf-8-sig")

df = df.dropna(subset=[TEXT_COLUMN, LABEL_COLUMN])
df[TEXT_COLUMN] = df[TEXT_COLUMN].astype(str)
df[LABEL_COLUMN] = df[LABEL_COLUMN].astype(str)

print("Tổng số mẫu:", len(df))
print("\nPhân bố label:")
print(df[LABEL_COLUMN].value_counts())


# =========================
# ENCODE LABEL
# =========================
label_encoder = LabelEncoder()
df["label_encoded"] = label_encoder.fit_transform(df[LABEL_COLUMN])

joblib.dump(label_encoder, f"{model_dir}/label_encoder.pkl")

print("\nDanh sách label:")
for idx, label in enumerate(label_encoder.classes_):
    print(idx, ":", label)


# =========================
# CHIA TRAIN / TEST
# =========================
train_df, test_df = train_test_split(
    df,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=df["label_encoded"]
)

train_df = train_df.reset_index(drop=True)
test_df = test_df.reset_index(drop=True)

# Lưu lại danh sách train/test cố định
train_df.to_csv(f"{split_dir}/train_set.csv", index=False, encoding="utf-8-sig")
test_df.to_csv(f"{split_dir}/test_set.csv", index=False, encoding="utf-8-sig")

print("\nĐã lưu train/test set:")
print(f"{split_dir}/train_set.csv")
print(f"{split_dir}/test_set.csv")

X_train = train_df[TEXT_COLUMN].astype(str)
y_train = train_df["label_encoded"].values

num_classes = len(label_encoder.classes_)


# ============================================================
# 1. TRAIN NAIVE BAYES + TF-IDF
# ============================================================
nb_model = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.9
    )),
    ("clf", MultinomialNB())
])

nb_model.fit(X_train, y_train)
joblib.dump(nb_model, f"{model_dir}/naive_bayes_tfidf.pkl")

print("\nĐã train và lưu Naive Bayes.")


# ============================================================
# 2. TRAIN SVM + TF-IDF
# ============================================================
svm_model = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.9
    )),
    ("clf", LinearSVC(class_weight="balanced"))
])

svm_model.fit(X_train, y_train)
joblib.dump(svm_model, f"{model_dir}/svm_tfidf.pkl")

print("Đã train và lưu SVM.")


# ============================================================
# TOKENIZER CHO CNN / LSTM
# ============================================================
tokenizer = Tokenizer(
    num_words=MAX_WORDS,
    oov_token="<OOV>"
)

tokenizer.fit_on_texts(X_train)

X_train_seq = tokenizer.texts_to_sequences(X_train)

X_train_pad = pad_sequences(
    X_train_seq,
    maxlen=MAX_LEN,
    padding="post",
    truncating="post"
)

joblib.dump(tokenizer, f"{model_dir}/tokenizer.pkl")

early_stop_cnn = EarlyStopping(
    monitor="val_loss",
    patience=3,
    restore_best_weights=True
)

early_stop_lstm = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)


# ============================================================
# 3. TRAIN CNN
# ============================================================
cnn_model = Sequential([
    Embedding(
        input_dim=MAX_WORDS,
        output_dim=EMBEDDING_DIM,
        input_length=MAX_LEN
    ),
    Conv1D(
        filters=128,
        kernel_size=5,
        activation="relu"
    ),
    GlobalMaxPooling1D(),
    Dropout(0.5),
    Dense(64, activation="relu"),
    Dropout(0.3),
    Dense(num_classes, activation="softmax")
])

cnn_model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer="adam",
    metrics=["accuracy"]
)

cnn_model.fit(
    X_train_pad,
    y_train,
    validation_split=0.2,
    epochs=15,
    batch_size=32,
    callbacks=[early_stop_cnn],
    verbose=1
)

cnn_model.save(f"{model_dir}/cnn_model.keras")

print("Đã train và lưu CNN.")


# ============================================================
# 4. TRAIN LSTM
# ============================================================
lstm_model = Sequential([
    Embedding(
        input_dim=MAX_WORDS,
        output_dim=EMBEDDING_DIM,
        input_length=MAX_LEN,
        mask_zero=True
    ),
    LSTM(128),
    Dropout(0.5),
    Dense(64, activation="relu"),
    Dropout(0.3),
    Dense(num_classes, activation="softmax")
])

lstm_model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer="adam",
    metrics=["accuracy"]
)

lstm_model.fit(
    X_train_pad,
    y_train,
    validation_split=0.2,
    epochs=15,
    batch_size=32,
    callbacks=[early_stop_lstm],
    verbose=1
)

lstm_model.save(f"{model_dir}/lstm_model.keras")

print("Đã train và lưu LSTM.")


print("\n==============================")
print("HOÀN THÀNH TRAIN 4 MÔ HÌNH")
print("Model lưu tại:", model_dir)
print("Train/Test lưu tại:", split_dir)
print("==============================")