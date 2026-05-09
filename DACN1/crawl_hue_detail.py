import os
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# =========================
# CẤU HÌNH
# =========================
input_path = "DACN1/hue_feedback_links.csv"
output_path = "DACN1/hue_feedback_details.csv"

os.makedirs("DACN1", exist_ok=True)


# =========================
# HÀM LẤY TEXT AN TOÀN
# =========================
def get_text_by_css(driver, selector):
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        return element.text.strip()
    except:
        return ""


def detect_status(page_text):
    page_text_lower = page_text.lower()

    if "kết quả xử lý" in page_text_lower:
        return "Đã xử lý"

    if "đã xử lý" in page_text_lower:
        return "Đã xử lý"

    if "đang xử lý" in page_text_lower:
        return "Đang xử lý"

    if "chưa xử lý" in page_text_lower:
        return "Chưa xử lý"

    return "Chưa xác định"


def clean_time(raw_time):
    # Ví dụ raw_time = "Ngày gửi: 08:00 09/02/2026"
    return raw_time.replace("Ngày gửi:", "").strip()


def clean_handler(raw_handler):
    # Xóa chữ thừa nếu có
    raw_handler = raw_handler.replace("Xử lý viên:", "").strip()
    raw_handler = raw_handler.replace("Đơn vị xử lý:", "").strip()
    return raw_handler


# =========================
# ĐỌC FILE LINK
# =========================
df_links = pd.read_csv(input_path)

if "url" not in df_links.columns:
    raise ValueError("File CSV phải có cột 'url'")

urls = df_links["url"].dropna().tolist()

print("Tổng số link cần xử lý:", len(urls))


# =========================
# SETUP SELENIUM
# =========================
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

data = []

try:
    for index, url in enumerate(urls, start=1):
        print(f"\nĐang xử lý {index}/{len(urls)}")
        print("URL:", url)

        try:
            driver.get(url)
            time.sleep(2)

            page_text = driver.find_element(By.TAG_NAME, "body").text

            # Lấy nội dung phản ánh
            content = get_text_by_css(driver, ".ChiTiet_NoiDung")

            # Lấy thời gian gửi
            raw_time = get_text_by_css(driver, ".ChiTiet_NgayGui")
            send_time = clean_time(raw_time)

            # Lấy xử lý viên / đơn vị xử lý
            raw_handler = get_text_by_css(driver, ".ChiTiet_XuLy_Vien")
            handler = clean_handler(raw_handler)

            # Lấy trạng thái
            status = detect_status(page_text)

            data.append({
                "id": index,
                "city": "Hue",
                "time": send_time,
                "content": content,
                "handler": handler,
                "status": status,
                "url": url
            })

        except Exception as e:
            print("Lỗi khi xử lý link:", e)

            data.append({
                "id": index,
                "city": "Hue",
                "time": "",
                "content": "",
                "handler": "",
                "status": "Lỗi",
                "url": url
            })

finally:
    driver.quit()


# =========================
# LƯU FILE
# =========================
df_result = pd.DataFrame(data)

df_result.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\n=========================")
print("HOÀN THÀNH")
print("Tổng số dòng:", len(df_result))
print("Đã lưu file:", output_path)
print("=========================")