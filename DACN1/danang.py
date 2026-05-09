import os
import re
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# =========================
# CẤU HÌNH
# =========================
output_path = "DACN1/hanoi_feedback_cards.csv"

os.makedirs("DACN1", exist_ok=True)


# =========================
# HÀM LẤY DỮ LIỆU TỪ CARD
# =========================
def extract_cards(driver, page):
    data = []

    cards = driver.find_elements(By.CSS_SELECTOR, ".issue-card")

    print(f"Số card tìm được: {len(cards)}")

    for card in cards:
        try:
            # Lấy tiêu đề + link chi tiết
            a_tag = card.find_element(By.CSS_SELECTOR, "a")
            title = a_tag.text.strip()
            url = a_tag.get_attribute("href")

            # Lấy mô tả ngắn
            try:
                description = card.find_element(By.CSS_SELECTOR, ".card-description").text.strip()
            except:
                description = ""

            # Lấy ID cuối link, ví dụ: ...-267033
            match = re.search(r"-(\d+)$", url or "")
            feedback_id = match.group(1) if match else ""

            # Ghép title + mô tả để làm dữ liệu NLP
            full_text = f"{title}. {description}".strip()

            data.append({
                "id": feedback_id,
                "city": "Ha Noi",
                "source": "congdanso_hanoi",
                "page": page,
                "title": title,
                "description": description,
                "full_text": full_text,
                "url": url
            })

        except Exception as e:
            print("Lỗi đọc card:", e)

    return data


# =========================
# SETUP CHROME
# =========================
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)

all_data = []
seen_urls = set()

try:
    # Mở trang chủ trước
    driver.get("https://congdanso.hanoi.gov.vn/")
    time.sleep(5)

    print("URL hiện tại:", driver.current_url)
    print("Title:", driver.title)

    input("Bro tự vào mục Phản ánh hiện trường -> Giao thông, sau đó nhấn Enter để bắt đầu crawl...")

    max_pages = 20  # test trước 20 trang, ổn thì tăng lên

    for page in range(1, max_pages + 1):
        print(f"\nĐang xử lý trang {page}...")

        time.sleep(2)

        page_data = extract_cards(driver, page)

        new_count = 0

        for item in page_data:
            url = item["url"]

            if url and url not in seen_urls:
                seen_urls.add(url)
                all_data.append(item)
                new_count += 1

        print(f"Số mẫu mới: {new_count}")
        print(f"Tổng mẫu hiện có: {len(all_data)}")

        # Cuộn xuống cuối trang để thấy phân trang
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # Click nút sang trang tiếp theo
        try:
            next_li = driver.find_element(By.CSS_SELECTOR, "li.ant-pagination-next")
            cls = next_li.get_attribute("class") or ""

            if "ant-pagination-disabled" in cls:
                print("Đã tới trang cuối.")
                break

            next_button = next_li.find_element(By.CSS_SELECTOR, "button")

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)

            driver.execute_script("arguments[0].click();", next_button)

            print("Đã click sang trang tiếp theo.")
            time.sleep(3)

        except Exception as e:
            print("Không click được nút next:", e)
            break

finally:
    driver.quit()


# =========================
# LƯU FILE CSV
# =========================
df = pd.DataFrame(all_data)

df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\n=========================")
print("HOÀN THÀNH")
print("Tổng số mẫu lấy được:", len(df))
print("Đã lưu file:", output_path)
print("=========================")