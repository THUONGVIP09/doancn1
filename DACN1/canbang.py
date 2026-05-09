import pandas as pd
import os

# =========================
# CẤU HÌNH
# =========================
input_path = "DACN1/feedback_labeled_augmented.csv"
output_path = "DACN1/feedback_labeled_balanced.csv"

MAX_PER_TOP_LABEL = 100
TOP_N_LABELS = 3
RANDOM_STATE = 42

os.makedirs("DACN1", exist_ok=True)

# =========================
# ĐỌC FILE
# =========================
df = pd.read_csv(input_path, encoding="utf-8-sig")

if "label" not in df.columns:
    raise ValueError("Không tìm thấy cột 'label' trong file CSV")

print("Phân bố label ban đầu:")
print(df["label"].value_counts())

# =========================
# TÌM 3 NHÃN NHIỀU MẪU NHẤT
# =========================
top_labels = df["label"].value_counts().head(TOP_N_LABELS).index.tolist()

print("\n3 nhãn nhiều mẫu nhất:")
print(top_labels)

# =========================
# LẤY TỐI ĐA 100 MẪU CHO 3 NHÃN ĐẦU
# CÁC NHÃN KHÁC GIỮ NGUYÊN
# =========================
balanced_parts = []

for label, group in df.groupby("label"):
    if label in top_labels:
        if len(group) > MAX_PER_TOP_LABEL:
            group_sampled = group.sample(
                n=MAX_PER_TOP_LABEL,
                random_state=RANDOM_STATE
            )
        else:
            group_sampled = group
    else:
        group_sampled = group

    balanced_parts.append(group_sampled)

balanced_df = pd.concat(balanced_parts, ignore_index=True)

# Xáo trộn lại toàn bộ dữ liệu
balanced_df = balanced_df.sample(
    frac=1,
    random_state=RANDOM_STATE
).reset_index(drop=True)

# =========================
# LƯU FILE
# =========================
balanced_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\n==============================")
print("HOÀN THÀNH CÂN BẰNG DỮ LIỆU")
print("File lưu tại:", output_path)
print("==============================")

print("\nPhân bố label sau khi xử lý:")
print(balanced_df["label"].value_counts())

print("\nTổng số mẫu ban đầu:", len(df))
print("Tổng số mẫu sau khi xử lý:", len(balanced_df))