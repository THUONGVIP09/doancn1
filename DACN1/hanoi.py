import os
import re
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


output_path = "DACN1/hanoi_feedback_cards.csv"
os.makedirs("DACN1", exist_ok=True)


def extract_cards(driver, page):
    data = []

    cards = driver.find_elements(By.CSS_SELECTOR, ".issue-card")

    print("Số card tìm được:", len(cards))

    for card in cards:
        try:
            # Lấy title + link
            a_tag = card.find_element(By.CSS_SELECTOR, "a")
            title = a_tag.text.strip()
            href = a_tag.get_attribute("href")

            # Lấy description
            try:
                desc = card.find_element(By.CSS_SELECTOR, ".card-description").text.strip()
            except:
                desc = ""

            # Lấy ID cuối URL nếu có
            match = re.search(r"-(\d+)$", href or "")
            feedback_id = match.group(1) if match else ""

            full_text = f"{title}. {desc}".strip()

            data.append({
                "id": feedback_id,
                "city": "Ha Noi",
                "source": "congdanso_hanoi",
                "page": page,
                "title": title,
                "description": desc,
                "full_text": full_text,
                "url": href
            })

        except Exception as e:
            print("Lỗi đọc card:", e)

    return data


options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = webdriver.Chrome(options=options)

all_data = []
seen_urls = set()

max_pages = 20  # test trước 20 trang, ổn thì tăng lên 100

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

    print("Số mẫu mới:", new_count)
    print("Tổng mẫu:", len(all_data))

    # Cuộn xuống cuối để hiện phân trang
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    try:
        next_li = driver.find_element(By.CSS_SELECTOR, "li.ant-pagination-next")
        cls = next_li.get_attribute("class") or ""

        if "ant-pagination-disabled" in cls:
            print("Đã tới trang cuối.")
            break

        next_button = next_li.find_element(By.CSS_SELECTOR, "button")
        driver.execute_script("arguments[0].click();", next_button)

        print("Đã click sang trang tiếp theo.")
        time.sleep(3)

    except Exception as e:
        print("Không click được next:", e)
        break


df = pd.DataFrame(all_data)
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\n======================")
print("HOÀN THÀNH")
print("Tổng số mẫu:", len(df))
print("Đã lưu:", output_path)
print("======================")