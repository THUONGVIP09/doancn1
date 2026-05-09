import os
import re
import unicodedata
import pandas as pd
from pyvi import ViTokenizer


# =========================
# CẤU HÌNH
# =========================
input_path = "DACN1/hanoi_feedback_cards.csv"
output_path = "DACN1/hanoi_feedback_preprocessed.csv"

TEXT_COLUMN = "content"

os.makedirs("DACN1", exist_ok=True)


# =========================
# HÀM CƠ BẢN
# =========================
def normalize_unicode(text):
    return unicodedata.normalize("NFC", str(text))


def clean_basic_text(text):
    if pd.isna(text):
        return ""

    text = str(text)
    text = normalize_unicode(text)

    # Xóa link, HTML entity
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"&nbsp;|&amp;|&lt;|&gt;|&quot;", " ", text)

    # Đưa xuống dòng thành khoảng trắng
    text = re.sub(r"[\n\r\t]+", " ", text)

    # Giữ chữ tiếng Việt, số và dấu cơ bản
    text = re.sub(r"[^a-zA-ZÀ-ỹ0-9\s\.,;:/\-\(\)_]", " ", text)

    # Giữ ngày tháng dạng 30/04
    text = re.sub(r"(\d{1,2})\s*/\s*(\d{1,2})", r"\1/\2", text)

    # Xử lý khoảng trắng
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"([,.;:])(?=[^\s])", r"\1 ", text)

    return text.strip()


# =========================
# XỬ LÝ ĐỊA ĐIỂM / TÊN RIÊNG
# =========================
def join_location_names(text):
    """
    Nối các cụm địa điểm/tên riêng viết hoa liên tục bằng dấu _.
    Ví dụ:
    cầu Trường Tiền -> cầu Trường_Tiền
    kiệt 32 Thiên Thai -> kiệt 32 Thiên_Thai
    Phường Thủy Xuân -> Phường_Thủy_Xuân
    Thành phố Huế -> Thành_phố_Huế
    """

    # 1. Nối cụm có tiền tố địa điểm + tên riêng
    location_pattern = (
        r"\b(cầu|đường|kiệt|hẻm|phường|xã|quận|huyện|thành phố|tp)\s+"
        r"(\d+\s+)?"
        r"([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+){0,5})"
    )

    def replace_location(match):
        prefix = match.group(1)
        number = match.group(2) or ""
        name = match.group(3)

        prefix_joined = prefix.replace(" ", "_")
        name_joined = name.replace(" ", "_")

        return f"{prefix_joined} {number}{name_joined}".strip()

    text = re.sub(location_pattern, replace_location, text)

    # 2. Nối các tên riêng viết hoa liên tục còn lại
    proper_name_pattern = r"\b[A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+){1,5}\b"

    def replace_proper_name(match):
        return match.group(0).replace(" ", "_")

    text = re.sub(proper_name_pattern, replace_proper_name, text)

    return text


# =========================
# DÙNG THƯ VIỆN TÁCH TỪ GHÉP
# =========================
def tokenize_compound_words(text):
    if not text:
        return ""

    try:
        return ViTokenizer.tokenize(text)
    except Exception:
        return text


# =========================
# TIỀN XỬ LÝ CHÍNH
# =========================
def preprocess_content(text):
    # 1. Làm sạch cơ bản
    clean_text = clean_basic_text(text)

    # 2. Nối địa điểm/tên riêng trước
    location_text = join_location_names(clean_text)

    # 3. Dùng ViTokenizer tìm từ ghép
    compound_text = tokenize_compound_words(location_text)

    # 4. Bản ML đưa về chữ thường
    ml_text = compound_text.lower()

    return clean_text, compound_text, ml_text


# =========================
# MAIN
# =========================
df = pd.read_csv(input_path)

if TEXT_COLUMN not in df.columns:
    raise ValueError(f"Không tìm thấy cột '{TEXT_COLUMN}' trong file CSV")

clean_contents = []
compound_contents = []
ml_texts = []

for text in df[TEXT_COLUMN].fillna(""):
    clean_text, compound_text, ml_text = preprocess_content(text)

    clean_contents.append(clean_text)
    compound_contents.append(compound_text)
    ml_texts.append(ml_text)

df["original_content"] = df[TEXT_COLUMN]
df["clean_content"] = clean_contents
df["compound_content"] = compound_contents
df["ml_text"] = ml_texts

df["is_empty_after_clean"] = df["clean_content"].apply(
    lambda x: len(str(x).strip()) == 0
)

df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("Đã tạo file:", output_path)
print("Tổng số dòng:", len(df))
print("Số dòng rỗng sau tiền xử lý:", df["is_empty_after_clean"].sum())

print("\nVí dụ trước/sau:")
for i in range(min(5, len(df))):
    print("=" * 100)
    print("Gốc      :", df.loc[i, "original_content"])
    print("Clean    :", df.loc[i, "clean_content"])
    print("Compound :", df.loc[i, "compound_content"])
    print("ML text  :", df.loc[i, "ml_text"])