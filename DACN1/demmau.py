import pandas as pd

# Đường dẫn file của bạn
file_path = "DACN1/model_outputs/splits/train_set.csv"

# Đọc file CSV
df = pd.read_csv(file_path, encoding="utf-8-sig")

# Kiểm tra có cột label không
if "label" not in df.columns:
    raise ValueError("Không tìm thấy cột 'label' trong file CSV")

# Đếm số lượng từng thể loại
label_counts = df["label"].value_counts()

print("Số lượng mẫu theo từng thể loại:")
print(label_counts)

# Nếu muốn lưu ra file CSV
label_counts.to_csv(
    "DACN1/label_counts.csv",
    header=["count"],
    encoding="utf-8-sig"
)

print("\nĐã lưu kết quả vào: DACN1/label_counts.csv")