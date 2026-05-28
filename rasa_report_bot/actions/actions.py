from importlib.metadata import metadata
from typing import Any, Text, Dict, List

import re
import requests

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from sqlalchemy import create_engine, text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/dacn1_db"

engine = create_engine(DATABASE_URL)

# =========================
# LOAD MODEL CNN
# =========================



def get_category_display_name(category: str) -> str:
    category_names = {
        "duong_cau_ha_tang_hu_hong": "Đường/cầu/hạ tầng hư hỏng",
        "dien_luc_chieu_sang": "Điện lực/chiếu sáng",
        "cong_ho_ga_thoat_nuoc": "Cống/hố ga/thoát nước",
        "via_he_long_duong": "Vỉa hè/lòng đường",
        "cay_xanh_vat_can": "Cây xanh/vật cản",
        "do_xe_can_tro": "Đỗ xe/cản trở",
        "den_tin_hieu": "Đèn tín hiệu",
        "bien_bao": "Biển báo",
        "to_chuc_giao_thong": "Tổ chức giao thông",
        "rac_thai_ve_sinh_moi_truong": "Rác thải/vệ sinh môi trường",
        "khac": "Khác"
    }

    return category_names.get(category, category)
def predict_category(content: str):
    """
    Gọi FastAPI của doancn1 để phân loại nội dung phản ánh bằng CNN.
    """

    API_URL = "http://localhost:8000/classify-text"

    try:
        response = requests.post(
            API_URL,
            json={
                "content": content
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        predicted_category = data.get("predicted_category", "khac")
        predicted_name = data.get("predicted_name", predicted_category)
        confidence = float(data.get("confidence", 0.0))

        return predicted_category, predicted_name, confidence

    except Exception as e:
        print("Lỗi khi gọi API phân loại:", e)
        return "khac", "Khác", 0.0



def find_duplicate_report(content: str, location: str, category: str):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT id, content, location, predicted_category
                FROM reports
                WHERE predicted_category = :category
                AND duplicate_of IS NULL
                ORDER BY created_at DESC
                LIMIT 50
            """),
            {"category": category}
        )

        old_reports = result.fetchall()

    if not old_reports:
        return None

    current_text = f"{content} {location}"

    old_texts = [
        f"{row.content} {row.location}"
        for row in old_reports
    ]

    all_texts = [current_text] + old_texts

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    max_score = similarities.max()
    max_index = similarities.argmax()

    duplicate_threshold = 0.55

    if max_score >= duplicate_threshold:
        duplicate_report = old_reports[max_index]
        return {
            "id": duplicate_report.id,
            "content": duplicate_report.content,
            "location": duplicate_report.location,
            "score": float(max_score)
        }

    return None


def save_report_to_db(content, location, category, predicted_name, confidence, duplicate_of=None, image_path=None):
    title = content[:100]

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO reports
                (title, content, location, image_path, predicted_category, predicted_name, status, confidence, duplicate_of)
                VALUES
                (:title, :content, :location, :image_path, :predicted_category, :predicted_name, :status, :confidence, :duplicate_of)
            """),
            {
                "title": title,
                "content": content,
                "location": location,
                "image_path": image_path,
                "predicted_category": category,
                "predicted_name": predicted_name,
                "status": "Chờ xử lý",
                "confidence": confidence,
                "duplicate_of": duplicate_of
            }
        )

        return result.lastrowid

def verify_location_with_vietmap(location_text: str):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/verify-location",
            json={"query": location_text},
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        if data.get("valid"):
            return data

        return None

    except Exception as e:
        print("Lỗi kiểm tra địa điểm bằng Vietmap:", e)
        return None


def clean_location_text(location: str):
    if not location:
        return None

    location = location.strip(" ,.-;:")

    # Cắt bỏ phần mô tả sự cố phía sau địa điểm
    stop_phrases = [
        " không nhảy",
        " không hoạt động",
        " không đếm",
        " không được bật",
        " không bật",
        " không sáng",
        " bị hỏng",
        " bị nghẹt",
        " bị ngập",
        " bị kẹt",
        " bị ngã",
        " chắn ngang",
        " có ổ gà",
        " có rác",
        " xuống cấp",
        " hư hỏng",
        " mất tín hiệu",
        " gây khó khăn",
        " gây nguy hiểm",
        " ảnh hưởng",
    ]

    location_lower = location.lower()

    cut_positions = []
    for phrase in stop_phrases:
        pos = location_lower.find(phrase)
        if pos != -1:
            cut_positions.append(pos)

    if cut_positions:
        location = location[:min(cut_positions)]

    # Bỏ từ mở đầu dư
    prefixes = [
        "vấn đề xảy ra ở ",
        "vấn đề xảy ra tại ",
        "sự việc xảy ra ở ",
        "sự việc xảy ra tại ",
        "địa điểm là ",
        "ở ",
        "tại ",
        "gần ",
        "khu vực ",
    ]

    location_lower = location.lower().strip()

    for prefix in prefixes:
        if location_lower.startswith(prefix):
            location = location[len(prefix):]
            break

    location = re.sub(r"\s+", " ", location).strip(" ,.-;:")

    if len(location) < 5:
        return None

    return location

def extract_location_from_text(text: str):
    if not text:
        return None

    text = text.strip().rstrip(".!? ").strip()

    # Các cụm này chứng tỏ câu đang mô tả sự cố, không phải địa chỉ
    invalid_location_phrases = [
        "đường dây điện",
        "dây điện",
        "cành cây",
        "nhánh cây",
        "cây vướng",
        "mùa mưa",
        "nguy hiểm",
        "gây nguy hiểm",
        "gây khó khăn",
        "không được bật",
        "không sáng",
        "không nhảy",
        "bị hỏng",
        "bị nghẹt",
        "bị ngập",
        "có ổ gà",
        "có rác",
    ]

    def is_valid_location(location: str):
        location_lower = location.lower()

        has_admin_place = any(
            key in location_lower
            for key in ["phường", "xã", "thị trấn", "quận", "huyện", "tỉnh", "thành phố", "ngã tư", "ngã ba", "cầu"]
        )

        has_invalid_phrase = any(
            phrase in location_lower
            for phrase in invalid_location_phrases
        )

        if has_invalid_phrase and not has_admin_place:
            return False

        if location_lower.startswith("đường dây điện"):
            return False

        if location_lower.startswith("đường nhiều"):
            return False

        if location_lower.startswith("đường có"):
            return False

        if location_lower.startswith("đường bị"):
            return False

        if location_lower.startswith("đường ngập"):
            return False

        return True

    patterns = [
        # Dạng rõ nhất: Đường Võ Văn Tần, phường Nguyệt Hoá, tỉnh Vĩnh Long
        r"((?:đường|cầu|ngã tư|ngã ba|vòng xoay)\s+.+?(?:,\s*)?(?:phường|xã|thị trấn)\s+.+?(?:,\s*)?(?:quận|huyện|thành phố|tỉnh)\s+[^.;\n]+)",

        # Dạng giao lộ: đường A giao đường B, phường X, tỉnh Y
        r"((?:đường|cầu|ngã tư|ngã ba|vòng xoay)\s+.+?(?:giao|giao với|cắt|cắt với)\s+(?:đường|cầu)?\s*.+?(?:,\s*)?(?:phường|xã|thị trấn)\s+.+?(?:,\s*)?(?:quận|huyện|thành phố|tỉnh)\s+[^.;\n]+)",

        # Dạng có phường/xã + tỉnh/thành phố
        r"((?:phường|xã|thị trấn)\s+.+?(?:tỉnh|thành phố)\s+[^.;\n]+)",

        # Dạng địa điểm có từ khóa rõ hơn
        r"((?:ngã tư|ngã ba|vòng xoay|cầu)\s+[^.;\n]+)",

        # Dạng đường nhưng phải có tên riêng phía sau, tránh bắt 'đường dây điện'
        r"((?:đường)\s+(?!dây điện|nhiều|có|bị|ngập|hư|xuống cấp)[A-ZÀ-ỴĐ][^.;\n,]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            location = clean_location_text(match.group(1))

            if location and len(location.split()) >= 2 and is_valid_location(location):
                return location

    return None
class ValidateReportForm(FormValidationAction):

    def name(self) -> str:
        return "validate_report_form"

    def validate_report_content(
        self,
        slot_value,
        dispatcher,
        tracker,
        domain,
    ):
        content = slot_value.strip()

        if len(content) < 10:
            dispatcher.utter_message(
                text="Nội dung phản ánh hơi ngắn, bạn vui lòng mô tả rõ hơn giúp tôi nhé."
            )
            return {
                "report_content": None
            }

        extracted_location = extract_location_from_text(content)

        print("CONTENT:", content)
        print("EXTRACTED LOCATION:", extracted_location)

        if extracted_location:
            dispatcher.utter_message(
                text=f"Tôi đã nhận diện địa điểm là: {extracted_location}."
            )
            verified_location = verify_location_with_vietmap(extracted_location)

            if verified_location:
                address = verified_location.get("address")
                dispatcher.utter_message(
                    text=f"Tôi đã nhận diện địa điểm là: {address}. Nếu chưa đúng, bạn có thể nhập lại địa điểm hoặc bấm 📍 Gửi vị trí."
                )
                return {
                    "report_content": content,
                    "report_location": address
                }

        # Nếu không tách được địa điểm hoặc Vietmap không xác nhận được
        # thì bắt buộc hỏi lại địa điểm
        return {
            "report_content": content,
            "report_location": None
        }
    def validate_report_location(
        self,
        slot_value,
        dispatcher,
        tracker,
        domain,
    ):
        location = clean_location_text(slot_value)

        if not location or len(location) < 5:
            dispatcher.utter_message(
                text="Địa điểm hơi ngắn, bạn vui lòng nhập rõ hơn hoặc bấm 📍 Gửi vị trí nhé."
            )
            return {
                "report_location": None
            }

        metadata = tracker.latest_message.get("metadata") or {}
        image_path = metadata.get("image_path")

        return {
            "report_location": location,
            "report_image_path": image_path
        }
class ActionConfirmReport(Action):

    def name(self) -> Text:
        return "action_confirm_report"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        content = tracker.get_slot("report_content")
        location = tracker.get_slot("report_location")
        image_path = tracker.get_slot("report_image_path")
        image_url = None
        if image_path:
            image_url = f"http://127.0.0.1:8000{image_path}"

        if not content or not location:
            dispatcher.utter_message(text="Thông tin phản ánh chưa đầy đủ. Bạn vui lòng nhập lại giúp tôi.")
            return []

        category, predicted_name, confidence = predict_category(content)

        duplicate = find_duplicate_report(
            content=content,
            location=location,
            category=category
        )

        if duplicate:
            report_id = save_report_to_db(
                content=content,
                location=location,
                category=category,
                predicted_name=predicted_name,
                confidence=confidence,
                duplicate_of=duplicate["id"],
                image_path=image_path
            )

            message = (
                f"Hệ thống đã ghi nhận phản ánh của bạn với mã #{report_id}.\n"
                f"Tuy nhiên, hệ thống phát hiện phản ánh này tương tự với phản ánh #{duplicate['id']}.\n"
                f"Địa điểm phản ánh cũ: {duplicate['location']}.\n"
                f"Mức độ giống nhau: {duplicate['score']:.2f}.\n"
                f"Phân loại: {predicted_name}.\n"
                f"Trạng thái: Chờ xử lý."
            )

        else:
            report_id = save_report_to_db(
                content=content,
                location=location,
                category=category,
                predicted_name=predicted_name,
                confidence=confidence,
                duplicate_of=None,
                image_path=image_path
            )

            message = (
                f"Tôi đã ghi nhận phản ánh của bạn.\n"
                f"Mã phản ánh: #{report_id}.\n"
                f"Phân loại: {predicted_name}.\n"
                f"Độ tin cậy: {confidence:.2%}.\n"
                f"Trạng thái: Chờ xử lý."
            )

            if image_url:
                dispatcher.utter_message(text=message, image=image_url)
            else:
                dispatcher.utter_message(text=message)

        return [
            SlotSet("report_content", None),
            SlotSet("report_location", None),
            SlotSet("report_image_path", None)
        ]
class ActionCheckReportStatus(Action):

    def name(self) -> Text:
        return "action_check_report_status"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        report_id = tracker.get_slot("report_id")
        location = tracker.get_slot("report_location")
        user_text = tracker.latest_message.get("text", "").strip()

        # =========================
        # 1. Bắt mã phản ánh từ câu người dùng
        # Ví dụ: "kiểm tra phản ánh số 17", "#17"
        # =========================
        if not report_id:
            user_text_clean = user_text.strip().lower()

            # Trường hợp người dùng chỉ nhập số, ví dụ: "17"
            if re.fullmatch(r"\d+", user_text_clean):
                report_id = user_text_clean

            # Trường hợp người dùng nhập "#17"
            elif re.fullmatch(r"#\d+", user_text_clean):
                report_id = user_text_clean.replace("#", "")

            # Trường hợp nhập đầy đủ: "kiểm tra phản ánh số 17"
            else:
                id_patterns = [
                    r"(?:mã phản ánh|phản ánh mã|phản ánh số|số phản ánh|mã|số)\s*#?\s*(\d+)",
                    r"(?:kiểm tra|tra cứu|xem)\s+(?:phản ánh|mã phản ánh)?\s*(?:số|mã)?\s*#?\s*(\d+)"
                ]

                for pattern in id_patterns:
                    match = re.search(pattern, user_text_clean)
                    if match:
                        report_id = match.group(1)
                        break

        # =========================
        # 2. Nếu có mã phản ánh thì tra cứu theo ID
        # =========================
        if report_id:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT id, title, content, location, predicted_name, status, confidence, created_at, duplicate_of
                        FROM reports
                        WHERE id = :id
                    """),
                    {"id": report_id}
                )

                report = result.fetchone()

            if not report:
                dispatcher.utter_message(
                    text=f"Không tìm thấy phản ánh có mã #{report_id}."
                )
                return [
                    SlotSet("report_id", None),
                    SlotSet("report_location", None)
                ]

            duplicate_text = ""
            if report.duplicate_of:
                duplicate_text = f"\nPhản ánh này được ghi nhận là tương tự với phản ánh #{report.duplicate_of}."

            message = (
                f"Thông tin phản ánh #{report.id}:\n"
                f"- Nội dung: {report.content}\n"
                f"- Địa điểm: {report.location}\n"
                f"- Phân loại: {report.predicted_name}\n"
                f"- Trạng thái: {report.status}\n"
                f"- Độ tin cậy: {float(report.confidence):.2%}"
                f"{duplicate_text}"
            )

            dispatcher.utter_message(text=message)

            return [
                SlotSet("report_id", None),
                SlotSet("report_location", None)
            ]

        # =========================
        # 3. Tách địa điểm từ câu người dùng
        # Ví dụ: "Kiểm tra phản ánh ở Ngã tư đường Võ Văn Kiệt"
        # =========================
        if not location:
            prefixes = [
                "kiểm tra phản ánh ở",
                "kiểm tra phản ánh tại",
                "kiểm tra phản ánh gần",
                "tra cứu phản ánh ở",
                "tra cứu phản ánh tại",
                "tra cứu phản ánh gần",
                "xem phản ánh ở",
                "xem phản ánh tại",
                "xem phản ánh gần",
                "phản ánh ở",
                "phản ánh tại",
                "phản ánh gần",
            ]

            user_text_lower = user_text.lower()

            for prefix in prefixes:
                if user_text_lower.startswith(prefix):
                    location = user_text[len(prefix):].strip()
                    break

        print("USER TEXT:", user_text)
        print("REPORT ID:", report_id)
        print("LOCATION:", location)

        # =========================
        # 4. Tra cứu theo địa điểm
        # =========================
        if location:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT id, content, location, predicted_name, status, created_at
                        FROM reports
                        WHERE LOWER(location) LIKE :location
                        ORDER BY created_at DESC
                        LIMIT 10
                    """),
                    {"location": f"%{location.lower()}%"}
                )

                reports = result.fetchall()

            if not reports:
                dispatcher.utter_message(
                    text=f"Không tìm thấy phản ánh nào tại khu vực: {location}."
                )
                return [
                    SlotSet("report_id", None),
                    SlotSet("report_location", None)
                ]

            message = f"Tìm thấy {len(reports)} phản ánh gần khu vực {location}:\n"

            for report in reports:
                message += (
                    f"\n#{report.id} - {report.predicted_name}\n"
                    f"Nội dung: {report.content}\n"
                    f"Địa điểm: {report.location}\n"
                    f"Trạng thái: {report.status}\n"
                )

            dispatcher.utter_message(text=message)

            return [
                SlotSet("report_id", None),
                SlotSet("report_location", None)
            ]

        # =========================
        # 5. Không có mã hoặc địa điểm
        # =========================
        dispatcher.utter_message(
            text="Bạn muốn tra cứu bằng mã phản ánh hay địa điểm? Ví dụ: 'kiểm tra phản ánh số 17' hoặc 'kiểm tra phản ánh ở trước cổng trường VKU'."
        )

        return [
            SlotSet("report_id", None),
            SlotSet("report_location", None)
        ]
    