import os
import time
import pandas as pd
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# =========================
# CẤU HÌNH
# =========================
list_url = "https://tuongtac.hue.gov.vn/chuyen-muc/ha-tang-do-thi-a3.html"

output_path = "DACN1/hue_feedback_links.csv"

os.makedirs("DACN1", exist_ok=True)


# =========================
# SETUP CHROME
# =========================
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

all_data = []
seen_urls = set()

try:
    driver.get(list_url)
    time.sleep(3)

    max_pages = 60  # test trước 20 trang

    for page in range(1, max_pages + 1):
        print(f"\nĐang xử lý trang {page}...")

        time.sleep(2)

        # Lấy tất cả link item
        items = driver.find_elements(By.CSS_SELECTOR, ".PhanAnhLV_TieuDe a")

        print("Số item tìm được:", len(items))

        new_count = 0

        for item in items:
            title = item.text.strip()
            href = item.get_attribute("href")

            # Nếu href là dạng /phan-anh/... thì nối với domain
            full_url = urljoin(driver.current_url, href)

            if full_url in seen_urls:
                continue

            seen_urls.add(full_url)
            new_count += 1

            all_data.append({
                "city": "Hue",
                "source": "hue_feedback",
                "page": page,
                "title": title,
                "url": full_url
            })

        print("Số link mới:", new_count)
        print("Tổng link:", len(all_data))

        # Tìm nút trang tiếp theo
        next_page = page + 1

        try:
            next_btn = driver.find_element(
                By.XPATH,
                f"//a[normalize-space(text())='{next_page}']"
            )

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", next_btn)

            print(f"Đã sang trang {next_page}")
            time.sleep(3)

        except Exception:
            print(f"Không tìm thấy nút trang {next_page}. Thử nút >>>")

            try:
                next_btn = driver.find_element(
                    By.XPATH,
                    "//a[contains(normalize-space(text()), '>>>') or contains(normalize-space(text()), '>>')]"
                )

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_btn)

                print("Đã click nút >>>")
                time.sleep(3)

            except Exception as e:
                print("Không click được trang tiếp theo. Dừng crawl.")
                break

finally:
    driver.quit()


# =========================
# LƯU CSV
# =========================
df = pd.DataFrame(all_data)
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\n=========================")
print("HOÀN THÀNH")
print("Tổng số link lấy được:", len(df))
print("Đã lưu file:", output_path)
print("=========================")