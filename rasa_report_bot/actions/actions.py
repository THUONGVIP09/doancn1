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


def save_report_to_db(content, location, category, predicted_name, confidence, duplicate_of=None):
    title = content[:80]

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
                "image_path": None,
                "predicted_category": category,
                "predicted_name": predicted_name,
                "status": "Chờ xử lý",
                "confidence": confidence,
                "duplicate_of": duplicate_of
            }
        )

        return result.lastrowid



def extract_location_from_text(text: str):
    """
    Tách địa điểm từ nội dung phản ánh.
    Ưu tiên địa chỉ hành chính, địa danh, tọa độ.
    Tránh bắt nhầm các cụm mô tả như: "trước nhà dân", "trước cổng", ...
    """

    if not text:
        return None

    text = text.strip()

    # 1. Bắt tọa độ dạng: 9°36'08.4"N 106°20'35.7"E, xã Long Vĩnh
    coord_pattern = r"(\d{1,2}°\d{1,2}'\d{1,2}(?:\.\d+)?\"?[NS]\s+\d{1,3}°\d{1,2}'\d{1,2}(?:\.\d+)?\"?[EW](?:,\s*[^.;\n\)]*)?)"
    coord_match = re.search(coord_pattern, text, flags=re.IGNORECASE)

    if coord_match:
        location = coord_match.group(1).strip(" ,.-;:()")
        if len(location) >= 8:
            return location

    # 2. Bắt phần trong ngoặc nếu có chứa xã/phường/quận/huyện/tỉnh hoặc tọa độ
    bracket_pattern = r"\(([^)]*(?:xã|phường|quận|huyện|tỉnh|thành phố|°)[^)]*)\)"
    bracket_match = re.search(bracket_pattern, text, flags=re.IGNORECASE)

    if bracket_match:
        location = bracket_match.group(1).strip(" ,.-;:")
        if len(location) >= 8:
            return location

    # 3. Bắt cụm bắt đầu từ "tại/ở/khu vực/gần/đoạn gần"
    # Không dùng "trước/sau" vì dễ bắt nhầm mô tả sự cố.
    patterns = [
        r"(?:địa chỉ|địa điểm|vị trí)\s*(?:là|:)?\s*([^.;\n]+)",
        r"(?:đoạn gần|gần|khu vực|tại|ở)\s+([^.;\n]+)",
        r"((?:đường|cầu|ngã tư|hẻm|kiệt|xã|phường|quận|huyện|tỉnh|thành phố)\s+[^.;\n]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            location = match.group(1).strip()

            # Cắt bớt phần mô tả nếu lẫn vào
            stop_words = [
                "bị", "có", "rơi", "gãy", "đổ", "hư", "nguy hiểm",
                "mùa mưa", "cho người dân"
            ]

            for word in stop_words:
                idx = location.lower().find(word)
                if idx > 0:
                    location = location[:idx].strip()

            location = location.strip(" ,.-;:()")

            # Tránh bắt quá ngắn kiểu "Trà"
            if len(location) >= 8 and len(location.split()) >= 2:
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

        extracted_location = extract_location_from_text(content)

        if extracted_location:
            dispatcher.utter_message(
                text=f"Tôi đã nhận diện địa điểm là: {extracted_location}"
            )

            return {
                "report_content": content,
                "report_location": extracted_location
            }

        return {
            "report_content": content
        }

    def validate_report_location(
        self,
        slot_value,
        dispatcher,
        tracker,
        domain,
    ):
        location = slot_value.strip()

        if len(location) < 5:
            dispatcher.utter_message(
                text="Địa điểm hơi ngắn, bạn vui lòng nhập rõ hơn giúp tôi nhé."
            )
            return {
                "report_location": None
            }

        return {
            "report_location": location
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
                duplicate_of=duplicate["id"]
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
                duplicate_of=None
            )

            message = (
                f"Tôi đã ghi nhận phản ánh của bạn.\n"
                f"Mã phản ánh: #{report_id}.\n"
                f"Phân loại: {predicted_name}.\n"
                f"Độ tin cậy: {confidence:.2%}.\n"
                f"Trạng thái: Chờ xử lý."
            )

        dispatcher.utter_message(text=message)

        return [
            SlotSet("report_content", None),
            SlotSet("report_location", None)
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
            match = re.search(r"#?\b(\d+)\b", user_text)
            if match:
                report_id = match.group(1)

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