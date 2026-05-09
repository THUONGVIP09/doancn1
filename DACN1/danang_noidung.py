import os
import re
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================
# CẤU HÌNH
# =========================
input_path = "DACN1/danang_feedback_ids.csv"
output_path = "DACN1/danang_feedback_details.csv"

MAX_ROWS = 300

os.makedirs("DACN1", exist_ok=True)


# =========================
# HÀM PHỤ
# =========================
def clean_text(text):
    text = str(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_text_js(driver, selector):
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        text = driver.execute_script("return arguments[0].innerText;", element)
        return clean_text(text)
    except:
        return ""


def extract_time(page_text):
    match = re.search(r"Ngày phản ánh:\s*([^\n]+)", page_text)
    if match:
        return clean_text(match.group(1))
    return ""


def extract_handler_from_reply_block(reply_block_text):
    # Lấy phần sau "Trả lời của:" đến trước nội dung trả lời
    match = re.search(
        r"Trả lời của:\s*(.+?)(?=Sau khi|Qua kiểm tra|Theo|Kính gửi|Nội dung|$)",
        reply_block_text,
        flags=re.IGNORECASE | re.DOTALL
    )
    if match:
        return clean_text(match.group(1))
    return ""


def detect_status(reply_content, page_text):
    reply_lower = str(reply_content).lower()
    page_lower = str(page_text).lower()

    # Ưu tiên kiểm tra "đang xử lý" trước
    processing_keywords = [
        "đang tiếp nhận",
        "đang xử lý",
        "đang kiểm tra",
        "đang phối hợp",
        "đang xác minh",
        "tiếp nhận và xử lý",
        "đang tiếp nhận và xử lý",
        "sẽ kiểm tra",
        "sẽ xử lý",
        "chuyển xử lý",
        "chuyển đến",
        "đề nghị đơn vị",
    ]

    for kw in processing_keywords:
        if kw in reply_lower or kw in page_lower:
            return "Đang xử lý"

    # Sau đó mới kiểm tra đã xử lý
    done_keywords = [
        "đã xử lý",
        "đã hoàn thành",
        "đã khắc phục",
        "đã sửa chữa",
        "đã kiểm tra",
        "đã tiến hành",
        "đã thực hiện",
        "đã lắp đặt",
        "đã thay thế",
        "đã dọn dẹp",
        "đã thu gom",
        "đã phản hồi",
        "đã nhận được sự đồng thuận",
        "trân trọng cảm ơn",
    ]

    for kw in done_keywords:
        if kw in reply_lower or kw in page_lower:
            return "Đã xử lý"

    # Nếu có reply_content nhưng không rõ đã xong hay chưa
    if reply_content:
        return "Đang xử lý"

    if "chưa xử lý" in page_lower:
        return "Chưa xử lý"

    return "Chưa xác định"
# =========================
# ĐỌC FILE LINK
# =========================
df_links = pd.read_csv(input_path, encoding="utf-8-sig")

if "detail_url" not in df_links.columns:
    raise ValueError("File CSV phải có cột 'detail_url'")

df_test = df_links.head(MAX_ROWS)

print("Tổng số link trong file:", len(df_links))
print("Số link test:", len(df_test))


# =========================
# SELENIUM
# =========================
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

data = []

try:
    for index, row in df_test.iterrows():
        feedback_id = row.get("id", index + 1)
        url = row.get("detail_url", "")

        print(f"\nĐang xử lý mẫu {len(data) + 1}/{len(df_test)}")
        print("ID:", feedback_id)
        print("URL:", url)

        try:
            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span.ykien-chitiet-noidung")
                )
            )

            time.sleep(1)

            page_text = driver.find_element(By.TAG_NAME, "body").text

            # Nội dung phản ánh
            content = get_text_js(
                driver,
                "span.ykien-chitiet-noidung"
            )

            # Nội dung trả lời xử lý
            reply_content = get_text_js(
                driver,
                "span.ykien-chitiet-noidung-traloi"
            )

            # Toàn bộ block trả lời
            reply_block_text = get_text_js(
                driver,
                "div.block-traloi"
            )

            # Đơn vị xử lý
            handler = extract_handler_from_reply_block(reply_block_text)

            if not handler:
                handler = extract_handler_from_reply_block(page_text)

            # Thời gian
            send_time = extract_time(page_text)

            # Trạng thái
            status = detect_status(reply_content, page_text)

            item = {
                "id": feedback_id,
                "city": "Da Nang",
                "time": send_time,
                "content": content,
                "reply_content": reply_content,
                "handler": handler,
                "status": status,
                "url": url
            }

            data.append(item)

            print("---- KẾT QUẢ ----")
            print("time:", send_time)
            print("content:", content[:300])
            print("reply_content:", reply_content[:300])
            print("handler:", handler)
            print("status:", status)

        except Exception as e:
            print("Lỗi khi xử lý link:", e)

            data.append({
                "id": feedback_id,
                "city": "Da Nang",
                "time": "",
                "content": "",
                "reply_content": "",
                "handler": "",
                "status": "Lỗi",
                "url": url
            })

finally:
    driver.quit()


# =========================
# LƯU FILE TEST
# =========================
df_result = pd.DataFrame(data)

df_result.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\n=========================")
print("HOÀN THÀNH TEST 5 MẪU")
print("Tổng số dòng:", len(df_result))
print("Đã lưu file:", output_path)
print("=========================")