import pandas as pd
import unicodedata
import re
import os


# =========================
# CẤU HÌNH
# =========================
input_path = "DACN1/hanoi_feedback_preprocessed.csv"
output_path = "DACN1/hanoi_feedback_labeled.csv"

TEXT_COLUMN = "clean_content"

os.makedirs("DACN1", exist_ok=True)

df = pd.read_csv(input_path)

if TEXT_COLUMN not in df.columns:
    raise ValueError(f"Không tìm thấy cột {TEXT_COLUMN} trong file CSV")


# =========================
# HÀM XỬ LÝ CHỮ
# =========================
def remove_accents(text):
    text = str(text).lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text


def clean_text_no_accents(text):
    text = remove_accents(text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_keyword(keyword):
    return clean_text_no_accents(keyword)


# =========================
# BỘ NHÃN + KEYWORD CỐ ĐỊNH
# =========================
LABEL_KEYWORDS = {
    "duong_cau_ha_tang_hu_hong": [
        "mặt đường", "hẻm", "kiệt", "cầu", "sụt lún", "sụp lún", "xuống cấp",
        "ổ gà", "ổ voi", "nâng cấp đường", "sửa chữa đường",
        "hư hỏng mặt đường", "đường hỏng", "đường xấu", "bê tông"
    ],

    "cong_ho_ga_thoat_nuoc": [
        "cống", "nắp cống", "hố ga", "nắp hố ga", "mương", "thoát nước",
        "ngập", "ngập nước", "tắc nghẽn", "kênh mương", "nước thải",
        "rãnh thoát nước", "hệ thống thoát nước"
    ],

    "dien_luc_chieu_sang": [
        "đèn đường", "điện chiếu sáng", "đèn chiếu sáng", "bóng đèn",
        "trụ đèn", "không sáng", "mất điện chiếu sáng", "đèn cao áp",
        "đèn không sáng", "đèn bị tắt"
    ],

    "den_tin_hieu": [
        "đèn tín hiệu", "đèn giao thông", "đèn xanh", "đèn đỏ",
        "đèn vàng", "cột đèn tín hiệu", "chu kỳ đèn", "pha đèn",
        "điều khiển đèn", "điều chỉnh đèn giao thông",
        "thời gian chờ đèn", "nút giao có đèn"
    ],

    "bien_bao": [
        "biển báo", "biển cấm", "biển báo giao thông", "biển một chiều",
        "biển chỉ dẫn", "bảng tên", "biển tên", "biển báo cấm đỗ",
        "biển cấm đỗ", "biển báo tốc độ", "biển báo nguy hiểm",
        "biển báo bị gãy", "biển báo bị che khuất", "lắp biển báo",
        "bổ sung biển báo", "bảng tên đường"
    ],

    "do_xe_can_tro": [
        "đỗ xe", "đậu xe", "dừng xe", "xe đỗ", "xe đậu",
        "cản trở giao thông", "chắn lối", "đỗ sai quy định",
        "đậu sai quy định", "bãi đỗ xe", "đậu đỗ"
    ],

    "to_chuc_giao_thong": [
        "tổ chức giao thông", "phân luồng", "một chiều", "cấm đường",
        "điều chỉnh giao thông", "nút giao", "vòng xuyến",
        "kẹt xe", "ùn tắc", "giao thông bất hợp lý",
        "lưu thông", "phân làn", "hướng đi", "cấm xe",
        "điều tiết giao thông"
    ],

    "via_he_long_duong": [
        "vỉa hè", "lòng đường", "lối đi bộ", "gạch lát", "bó vỉa",
        "lấn chiếm", "chiếm vỉa hè", "lề đường", "hành lang an toàn"
    ],

    "cay_xanh_vat_can": [
        "cây xanh", "cành cây", "cây ngã", "cây đổ", "dây điện",
        "vật cản", "che khuất", "nghiêng đổ", "trụ điện ngã",
        "dây cáp", "dây viễn thông", "chướng ngại vật"
    ],

    "rac_thai_ve_sinh_moi_truong": [
        "rác", "rác thải", "vệ sinh", "ô nhiễm", "mùi hôi", "nước thải",
        "tập kết rác", "xả rác", "rác sinh hoạt"
    ]
}


LABEL_PRIORITY = [
    "den_tin_hieu",
    "bien_bao",
    "do_xe_can_tro",
    "to_chuc_giao_thong",
    "den_chieu_sang_hong",
    "cong_ho_ga_thoat_nuoc",
    "duong_cau_ha_tang_hu_hong",
    "via_he_long_duong",
    "cay_xanh_vat_can",
    "rac_thai_ve_sinh_moi_truong",
]


# =========================
# DỰ ĐOÁN 1 NHÃN DUY NHẤT
# =========================
def predict_label(text):
    text_norm = clean_text_no_accents(text)

    results = []

    for label, keywords in LABEL_KEYWORDS.items():
        score = 0

        for kw in keywords:
            kw_norm = normalize_keyword(kw)

            if kw_norm and kw_norm in text_norm:
                weight = len(kw_norm.split())
                score += max(1, weight)

        if score > 0:
            results.append({
                "label": label,
                "score": score
            })

    if not results:
        return "khac"

    def sort_key(item):
        label = item["label"]
        priority_index = LABEL_PRIORITY.index(label) if label in LABEL_PRIORITY else 999
        return (-item["score"], priority_index)

    best = sorted(results, key=sort_key)[0]

    return best["label"]


# =========================
# DỰ ĐOÁN PRIORITY
# =========================
def predict_priority(text):
    text_norm = clean_text_no_accents(text)

    high_keywords = [
        "nguy hiem", "mat an toan", "tai nan", "sup", "be nap",
        "gay do", "roi xuong", "ngap nang", "un tac nghiem trong",
        "tre em", "hoc sinh", "quoc lo", "nga tu",
        "den tin hieu khong hoat dong", "den giao thong bi hong"
    ]

    medium_keywords = [
        "can tro", "hu hong", "xuong cap", "do xe", "bien bao",
        "den giao thong", "den tin hieu", "nap cong", "via he",
        "long duong", "o ga", "sut lun"
    ]

    for kw in high_keywords:
        if kw in text_norm:
            return "cao"

    for kw in medium_keywords:
        if kw in text_norm:
            return "trung_binh"

    return "thap"


# =========================
# AUTO LABEL
# =========================
labels = []
priorities = []

for _, row in df.iterrows():
    text = str(row.get(TEXT_COLUMN, ""))

    labels.append(predict_label(text))
    priorities.append(predict_priority(text))


# =========================
# CHỈ LƯU KẾT QUẢ CUỐI CÙNG
# =========================
keep_columns = []

for col in [
    "id", "city", "time", "content",
    "clean_content", "compound_content", "ml_text",
    "handler", "status", "url"
]:
    if col in df.columns:
        keep_columns.append(col)

result_df = df[keep_columns].copy()

result_df["label"] = labels
result_df["priority"] = priorities

result_df.to_csv(output_path, index=False, encoding="utf-8-sig")


print("\n==============================")
print("HOÀN THÀNH AUTO LABEL")
print("File kết quả:", output_path)
print("==============================")

print("\nPhân bố label:")
print(result_df["label"].value_counts())

print("\nPhân bố priority:")
print(result_df["priority"].value_counts())

print("\nSố dòng nhãn khac:")
print((result_df["label"] == "khac").sum())