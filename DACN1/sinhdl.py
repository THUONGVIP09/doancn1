import os
import random
import pandas as pd

try:
    from pyvi import ViTokenizer
except Exception:
    ViTokenizer = None


# =========================
# CẤU HÌNH
# =========================
input_path = "DACN1/hue_feedback_labeled1.csv"
synthetic_output_path = "DACN1/synthetic_feedback.csv"
combined_output_path = "DACN1/feedback_labeled_augmented.csv"

os.makedirs("DACN1", exist_ok=True)

df = pd.read_csv(input_path, encoding="utf-8-sig")


# =========================
# MỤC TIÊU CÂN BẰNG
# =========================
TARGET_COUNT = 80

labels_to_augment = [
    "do_xe_can_tro",
    "den_tin_hieu",
    "bien_bao",
    "to_chuc_giao_thong",
    "rac_thai_ve_sinh_moi_truong",
]


# =========================
# HÀM TÁCH TỪ CHO ml_text
# =========================
def make_ml_text(text):
    if ViTokenizer is not None:
        try:
            return ViTokenizer.tokenize(text).lower()
        except Exception:
            return text.lower()
    return text.lower()


# =========================
# DỮ LIỆU ẢO THEO TEMPLATE
# =========================


hanoi_locations = [
    "ngõ 93 Hoàng Văn Thái, phường Khương Trung, quận Thanh Xuân",
    "đường Nguyễn Trãi, đoạn gần Ngã Tư Sở, quận Thanh Xuân",
    "phố Chùa Bộc, phường Quang Trung, quận Đống Đa",
    "đường Xuân Thủy, đoạn trước cổng Trường Đại học Quốc gia Hà Nội, quận Cầu Giấy",
    "phố Trần Duy Hưng, phường Trung Hòa, quận Cầu Giấy",
    "đường Láng, đoạn gần cầu vượt Láng Hạ, quận Đống Đa",
    "phố Kim Mã, phường Ngọc Khánh, quận Ba Đình",
    "đường Giải Phóng, đoạn gần bến xe Giáp Bát, quận Hoàng Mai",
    "phố Minh Khai, phường Vĩnh Tuy, quận Hai Bà Trưng",
    "đường Nguyễn Văn Cừ, phường Bồ Đề, quận Long Biên",
    "phố Đội Cấn, phường Liễu Giai, quận Ba Đình",
    "đường Hồ Tùng Mậu, phường Mai Dịch, quận Cầu Giấy",
    "phố Tôn Đức Thắng, phường Hàng Bột, quận Đống Đa",
    "đường Cầu Giấy, đoạn gần chợ Cầu Giấy, quận Cầu Giấy",
    "phố Bạch Mai, phường Bạch Mai, quận Hai Bà Trưng",
    "đường Lê Văn Lương, phường Nhân Chính, quận Thanh Xuân",
    "phố Nguyễn Xiển, phường Thanh Xuân Trung, quận Thanh Xuân",
    "đường Phạm Văn Đồng, đoạn gần công viên Hòa Bình, quận Bắc Từ Liêm",
    "phố Tây Sơn, đoạn gần Đại học Thủy Lợi, quận Đống Đa",
    "đường Hoàng Quốc Việt, phường Nghĩa Đô, quận Cầu Giấy",
]


def add_random_place(template):
    return template.format(place=random.choice(hanoi_locations))


synthetic_templates = {
    "do_xe_can_tro": [
        "Tại khu vực {place}, nhiều xe ô tô thường xuyên dừng đỗ dưới lòng đường trong thời gian dài, đặc biệt vào giờ cao điểm. Việc này làm thu hẹp phần đường lưu thông, gây khó khăn cho các phương tiện qua lại và tiềm ẩn nguy cơ mất an toàn giao thông. Kính đề nghị cơ quan chức năng kiểm tra và có biện pháp xử lý.",
        "Người dân phản ánh tại {place} xuất hiện tình trạng xe ô tô đỗ chắn trước lối ra vào khu dân cư. Các phương tiện khác khi đi qua phải lấn sang làn đối diện, gây cản trở giao thông và dễ xảy ra va chạm. Đề nghị lực lượng chức năng kiểm tra, nhắc nhở và xử lý tình trạng đỗ xe sai quy định.",
        "Khu vực {place} thường xuyên có xe tải, xe con dừng đỗ không đúng nơi quy định, đặc biệt vào buổi sáng và chiều tối. Tình trạng này gây ùn ứ cục bộ, ảnh hưởng đến việc đi lại của người dân và học sinh. Kính mong cơ quan chức năng sớm có phương án xử lý.",
        "Tại {place}, nhiều xe máy và ô tô đậu đỗ tràn xuống lòng đường, làm người đi bộ và phương tiện lưu thông gặp nhiều khó khăn. Một số thời điểm xe buýt và xe cứu thương khó di chuyển qua khu vực này. Đề nghị kiểm tra và bố trí biển cấm đỗ xe nếu cần thiết.",
        "Người dân tại {place} phản ánh tình trạng xe ô tô đỗ ngay tại khúc cua, làm khuất tầm nhìn của người tham gia giao thông. Việc này diễn ra thường xuyên và có nguy cơ gây tai nạn, đặc biệt vào ban đêm. Đề nghị cơ quan chức năng xử lý để đảm bảo an toàn.",
        "Tại khu vực {place}, nhiều xe ô tô đỗ thành hàng dài dưới lòng đường vào buổi tối, khiến các phương tiện đi qua phải di chuyển rất chậm. Người dân nhiều lần nhắc nhở nhưng tình trạng vẫn tiếp diễn. Đề nghị cơ quan chức năng kiểm tra và xử lý việc đỗ xe sai quy định.",
        "Người dân phản ánh tại {place} thường xuyên có xe giao hàng dừng đỗ ngay trước lối ra vào khu dân cư. Việc này gây cản trở sinh hoạt, đặc biệt vào giờ đi làm và giờ tan học. Kính đề nghị lực lượng chức năng có biện pháp chấn chỉnh.",
        "Khu vực {place} có nhiều ô tô đỗ sát hai bên đường, làm lòng đường bị thu hẹp đáng kể. Khi có xe lớn đi qua, các phương tiện ngược chiều gần như không thể lưu thông. Đề nghị kiểm tra và xem xét cắm biển cấm dừng đỗ tại vị trí này.",
        "Tại {place}, xe ô tô thường xuyên đậu ngay trước điểm giao cắt, gây khuất tầm nhìn cho người điều khiển xe máy. Tình trạng này tiềm ẩn nguy cơ va chạm giao thông. Kính mong cơ quan chức năng xử lý để đảm bảo an toàn.",
        "Người dân tại {place} phản ánh nhiều xe cá nhân đỗ lấn chiếm lòng đường trong thời gian dài, gây ùn ứ cục bộ vào giờ cao điểm. Đề nghị kiểm tra, nhắc nhở và xử phạt các trường hợp vi phạm.",
        "Tại khu vực {place}, xe taxi và xe công nghệ thường xuyên dừng đỗ để đón trả khách, gây cản trở dòng phương tiện đang lưu thông. Đề nghị bố trí điểm dừng phù hợp hoặc tăng cường kiểm tra trật tự giao thông.",
        "Nhiều xe ô tô đỗ chắn gần cổng cơ quan tại {place}, khiến người đi bộ phải di chuyển xuống lòng đường. Việc này gây mất an toàn, nhất là vào thời điểm đông phương tiện. Đề nghị cơ quan chức năng sớm xử lý.",
        "Tại {place}, tình trạng xe tải đỗ qua đêm dưới lòng đường diễn ra thường xuyên, làm ảnh hưởng đến việc lưu thông và vệ sinh khu vực. Kính đề nghị kiểm tra và có biện pháp xử lý dứt điểm."
    ],
    

    "den_tin_hieu": [
        "Đèn tín hiệu giao thông tại khu vực {place} hoạt động không ổn định, có thời điểm không chuyển pha đúng chu kỳ. Việc này khiến các phương tiện di chuyển lộn xộn, dễ xảy ra va chạm tại nút giao. Kính đề nghị đơn vị quản lý kiểm tra và khắc phục sớm.",
        "Tại nút giao gần {place}, thời gian chờ đèn đỏ quá lâu trong khi lượng phương tiện lưu thông rất lớn. Vào giờ cao điểm, tình trạng này gây ùn tắc kéo dài và ảnh hưởng đến các tuyến đường lân cận. Đề nghị cơ quan chức năng xem xét điều chỉnh chu kỳ đèn cho phù hợp.",
        "Người dân phản ánh đèn tín hiệu tại {place} bị lỗi, đèn xanh và đèn đỏ chuyển pha không hợp lý. Một số phương tiện không xác định được hướng di chuyển an toàn, gây mất trật tự giao thông. Đề nghị kiểm tra hệ thống điều khiển đèn tín hiệu tại khu vực này.",
        "Đèn tín hiệu dành cho người đi bộ tại {place} không hoạt động, khiến người dân gặp khó khăn khi sang đường. Khu vực này có nhiều học sinh, người đi bộ và phương tiện qua lại nên nguy cơ mất an toàn khá cao. Kính mong cơ quan chức năng sớm sửa chữa.",
        "Tại {place}, đèn vàng nhấp nháy liên tục trong nhiều khung giờ, trong khi mật độ phương tiện rất đông. Việc thiếu tín hiệu điều khiển rõ ràng khiến giao thông tại nút giao trở nên lộn xộn. Đề nghị kiểm tra và khôi phục hoạt động bình thường của đèn tín hiệu.",
        "Đèn tín hiệu tại khu vực {place} có hiện tượng chập chờn, lúc hoạt động lúc không, khiến người tham gia giao thông khó quan sát. Vào giờ cao điểm, các phương tiện di chuyển lộn xộn và dễ xảy ra va chạm. Đề nghị đơn vị quản lý kiểm tra hệ thống đèn.",
        "Tại nút giao gần {place}, đèn tín hiệu giao thông bị mất pha xanh theo một hướng, làm các phương tiện phải chờ rất lâu. Tình trạng này gây ùn tắc kéo dài trong nhiều khung giờ. Kính đề nghị điều chỉnh và sửa chữa kịp thời.",
        "Người dân phản ánh đèn đỏ tại {place} sáng quá lâu trong khi các hướng còn lại ít phương tiện. Việc phân bổ thời gian đèn chưa hợp lý gây lãng phí thời gian và ùn ứ cục bộ. Đề nghị khảo sát lại chu kỳ đèn.",
        "Đèn tín hiệu cho người đi bộ tại {place} bị mờ và khó quan sát vào ban ngày. Người dân, đặc biệt là học sinh và người lớn tuổi, gặp khó khăn khi sang đường. Đề nghị kiểm tra và thay thế thiết bị nếu cần.",
        "Tại {place}, đèn giao thông không đồng bộ với lưu lượng phương tiện thực tế. Một số thời điểm xe từ đường nhánh phải chờ quá lâu, dẫn đến tình trạng vượt đèn đỏ. Đề nghị cơ quan chức năng điều chỉnh chu kỳ hoạt động.",
        "Đèn tín hiệu tại khu vực {place} bị nghiêng, hướng đèn không còn quay đúng về phía người điều khiển phương tiện. Việc này khiến tài xế khó quan sát tín hiệu từ xa. Đề nghị kiểm tra lại vị trí lắp đặt.",
        "Tại {place}, đèn vàng nhấp nháy liên tục trong thời gian dài dù đây là khu vực có mật độ xe lớn. Việc thiếu điều khiển giao thông rõ ràng gây mất trật tự và tiềm ẩn nguy hiểm. Kính đề nghị khôi phục hoạt động bình thường của đèn.",
        "Người dân phản ánh đèn tín hiệu tại {place} thường xuyên bị che khuất bởi biển quảng cáo và cây xanh. Các phương tiện đi từ xa khó nhận biết tín hiệu, nhất là vào buổi tối. Đề nghị kiểm tra và xử lý vật che khuất."
    
    ],

    "bien_bao": [
        "Biển báo giao thông tại khu vực {place} bị cây xanh che khuất, người điều khiển phương tiện rất khó quan sát từ xa. Tình trạng này có thể khiến người đi đường không nhận biết được quy định giao thông tại khu vực. Kính đề nghị cơ quan chức năng cắt tỉa cây xanh và điều chỉnh lại vị trí biển báo.",
        "Tại {place}, biển cấm dừng đỗ bị nghiêng và nội dung trên biển đã mờ, gây khó khăn cho người tham gia giao thông. Một số phương tiện vẫn dừng đỗ tại khu vực này do không nhìn rõ biển báo. Đề nghị kiểm tra, thay thế hoặc sơn sửa lại biển báo.",
        "Người dân phản ánh khu vực {place} thiếu biển cảnh báo nguy hiểm tại đoạn đường cong, nơi thường xuyên có phương tiện di chuyển với tốc độ cao. Việc thiếu biển báo khiến người đi đường khó chủ động giảm tốc độ. Đề nghị bổ sung biển cảnh báo để đảm bảo an toàn giao thông.",
        "Bảng tên đường tại {place} bị hư hỏng và không còn rõ chữ, gây khó khăn cho người dân, shipper và phương tiện tìm địa chỉ. Kính đề nghị đơn vị quản lý kiểm tra và thay mới bảng tên đường để thuận tiện cho việc nhận diện địa điểm.",
        "Tại khu vực {place}, biển báo giao thông bị xoay lệch hướng so với chiều di chuyển của phương tiện. Người tham gia giao thông khó nhận biết nội dung biển, dễ đi sai quy định. Đề nghị cơ quan chức năng điều chỉnh lại vị trí biển báo.",
        "Biển cảnh báo tại {place} đã bị mờ chữ và xuống cấp sau thời gian dài sử dụng. Vào ban đêm hoặc khi trời mưa, người đi đường gần như không nhìn rõ nội dung. Kính đề nghị thay mới biển báo để đảm bảo an toàn.",
        "Người dân phản ánh tại {place} thiếu biển cảnh báo khu vực đông học sinh qua đường. Vào giờ tan học, phương tiện di chuyển nhiều nhưng không có cảnh báo giảm tốc độ. Đề nghị bổ sung biển báo phù hợp.",
        "Tại {place}, biển cấm đỗ xe được đặt quá sát góc khuất nên nhiều tài xế không quan sát được. Tình trạng dừng đỗ sai quy định vẫn diễn ra thường xuyên. Đề nghị xem xét đặt lại biển ở vị trí dễ nhìn hơn.",
        "Bảng tên đường tại khu vực {place} bị cây xanh che khuất, người dân và người tham gia giao thông khó xác định địa chỉ. Đề nghị cắt tỉa cây và chỉnh trang lại bảng tên đường.",
        "Biển báo hạn chế tốc độ tại {place} bị nghiêng và có dấu hiệu hư hỏng. Nhiều phương tiện đi qua không nhận biết được tốc độ cho phép. Đề nghị kiểm tra, sửa chữa hoặc thay thế biển báo.",
        "Tại khu vực {place}, cần bổ sung biển chỉ dẫn hướng đi do nhiều phương tiện thường xuyên đi nhầm làn và quay đầu không đúng vị trí. Việc này gây cản trở giao thông vào giờ cao điểm.",
        "Người dân kiến nghị lắp thêm biển cảnh báo đoạn đường hẹp tại {place}. Hiện nay xe ô tô và xe máy đi ngược chiều dễ xảy ra va chạm do thiếu biển nhắc nhở giảm tốc độ."
        "Tại khu vực {place}, biển báo một chiều được đặt ở vị trí chưa dễ quan sát, đặc biệt đối với người đi từ các tuyến nhánh ra đường chính. Điều này dễ dẫn đến tình trạng đi ngược chiều ngoài ý muốn. Đề nghị xem xét điều chỉnh vị trí đặt biển báo.",
    ],

    "to_chuc_giao_thong": [
        "Tổ chức giao thông tại khu vực {place} hiện chưa hợp lý, đặc biệt vào giờ cao điểm khi lượng phương tiện tăng cao. Các luồng xe giao cắt nhau nhiều, dễ gây ùn tắc và mất an toàn. Kính đề nghị cơ quan chức năng khảo sát và điều chỉnh phương án phân luồng.",
        "Người dân kiến nghị xem xét điều chỉnh hướng lưu thông tại {place} do tuyến đường thường xuyên xảy ra ùn tắc cục bộ. Việc tổ chức giao thông hiện nay chưa phù hợp với mật độ phương tiện thực tế. Đề nghị nghiên cứu phương án phân làn hoặc điều tiết giao thông hiệu quả hơn.",
        "Tại nút giao gần {place}, các phương tiện từ nhiều hướng cùng nhập vào một điểm gây xung đột giao thông. Vào giờ cao điểm, xe máy và ô tô thường xuyên chen lấn, làm tình trạng ùn tắc kéo dài. Đề nghị cơ quan chức năng xem xét tổ chức lại luồng xe.",
        "Khu vực {place} có nhiều trường học, cửa hàng và khu dân cư nhưng chưa có phương án điều tiết giao thông phù hợp. Người dân đề nghị bổ sung biển hướng dẫn, phân làn hoặc điều chỉnh chiều lưu thông để hạn chế ùn tắc và đảm bảo an toàn.",
        "Việc cấm rẽ hoặc hạn chế lưu thông tại khu vực {place} hiện gây bất tiện cho người dân sinh sống xung quanh. Nhiều phương tiện phải đi vòng xa, làm tăng áp lực giao thông lên các tuyến đường lân cận. Kính đề nghị xem xét lại phương án tổ chức giao thông.",
        "Tại khu vực {place}, lưu lượng phương tiện tăng cao nhưng cách tổ chức giao thông hiện nay chưa phù hợp. Xe từ nhiều hướng giao cắt liên tục, gây ùn tắc và mất an toàn. Đề nghị cơ quan chức năng khảo sát phương án điều tiết lại.",
        "Người dân phản ánh việc phân làn tại {place} chưa rõ ràng, khiến xe máy và ô tô thường xuyên đi lẫn vào nhau. Tình trạng này gây nguy hiểm, nhất là vào giờ cao điểm. Đề nghị kẻ lại vạch sơn và bổ sung hướng dẫn giao thông.",
        "Khu vực {place} thường xuyên ùn tắc do phương tiện rẽ trái, rẽ phải cùng lúc tại một điểm. Đề nghị xem xét điều chỉnh hướng lưu thông hoặc bố trí đèn tín hiệu riêng cho từng luồng xe.",
        "Tại {place}, phương án tổ chức giao thông một chiều hiện gây bất tiện cho người dân trong khu vực. Nhiều phương tiện phải đi vòng xa, làm tăng áp lực lên các tuyến đường nhỏ. Kính đề nghị xem xét điều chỉnh phù hợp hơn.",
        "Người dân kiến nghị bố trí lại luồng xe tại {place} vì tình trạng xung đột giữa xe đi thẳng và xe quay đầu diễn ra thường xuyên. Nếu không điều chỉnh, khu vực này dễ xảy ra tai nạn trong giờ cao điểm.",
        "Tại khu vực {place}, việc cho phép dừng đỗ gần nút giao gây ảnh hưởng đến luồng xe chính. Đề nghị kết hợp điều chỉnh tổ chức giao thông và tăng cường kiểm tra dừng đỗ sai quy định.",
        "Đề nghị nghiên cứu mở thêm hướng rẽ hoặc điều chỉnh biển hướng dẫn tại {place} để giảm tình trạng ùn tắc kéo dài. Hiện nay người dân di chuyển qua khu vực này mất nhiều thời gian vào buổi sáng.",
        "Tuyến đường qua {place} có mật độ phương tiện lớn nhưng chưa có phương án phân luồng hợp lý cho xe máy và ô tô. Đề nghị cơ quan chức năng khảo sát thực tế và điều chỉnh tổ chức giao thông."
    
    ],

    "rac_thai_ve_sinh_moi_truong": [
        "Tại khu vực {place}, rác thải sinh hoạt bị tập kết lâu ngày bên lề đường nhưng chưa được thu gom kịp thời. Tình trạng này gây mùi hôi, ảnh hưởng đến mỹ quan đô thị và sinh hoạt của người dân xung quanh. Kính đề nghị đơn vị vệ sinh môi trường kiểm tra và xử lý.",
        "Người dân phản ánh tại {place} thường xuyên xuất hiện tình trạng xả rác bừa bãi trên vỉa hè và gần miệng cống thoát nước. Khi trời mưa, rác trôi xuống cống gây tắc nghẽn và ứ đọng nước. Đề nghị tăng cường thu gom rác và tuyên truyền giữ gìn vệ sinh.",
        "Khu vực {place} có điểm tập kết rác không đúng nơi quy định, nhiều bao rác bị để tràn ra lòng đường. Việc này gây mất vệ sinh môi trường, phát sinh mùi hôi và ảnh hưởng đến người đi bộ. Đề nghị cơ quan chức năng kiểm tra và bố trí điểm tập kết phù hợp hơn.",
        "Tại {place}, nước thải từ một số hộ kinh doanh chảy ra mặt đường, gây mùi khó chịu và làm trơn trượt khu vực đi lại. Người dân lo ngại tình trạng này kéo dài sẽ ảnh hưởng đến vệ sinh môi trường và an toàn giao thông. Kính đề nghị kiểm tra, nhắc nhở và xử lý.",
        "Rác thải xây dựng bị đổ tại khu vực {place}, chiếm một phần vỉa hè và gây bụi bẩn. Người đi bộ phải di chuyển xuống lòng đường, tiềm ẩn nguy cơ mất an toàn. Đề nghị cơ quan chức năng yêu cầu thu dọn và xử lý hành vi đổ rác không đúng quy định.",
        "Sau các buổi họp chợ tự phát tại {place}, rác thải thường bị bỏ lại trên vỉa hè và lòng đường. Tình trạng này gây mất mỹ quan đô thị, ảnh hưởng đến môi trường sống của người dân. Đề nghị có biện pháp thu gom và kiểm soát việc buôn bán tại khu vực này.",
        "Tại khu vực {place}, rác thải sinh hoạt bị để tràn ra vỉa hè trong nhiều ngày, gây mùi hôi và ảnh hưởng đến người đi bộ. Một số bao rác bị rách, nước thải chảy xuống lòng đường. Đề nghị đơn vị vệ sinh môi trường thu gom kịp thời.",
        "Người dân phản ánh tại {place} có tình trạng đổ trộm rác thải xây dựng vào ban đêm. Vật liệu thừa chiếm một phần vỉa hè và gây bụi bẩn cho khu dân cư. Kính đề nghị kiểm tra và xử lý hành vi vi phạm.",
        "Khu vực {place} thường xuyên có rác tồn đọng quanh miệng cống thoát nước. Khi trời mưa, rác trôi xuống cống gây tắc nghẽn và ngập cục bộ. Đề nghị tăng cường thu gom và vệ sinh khu vực này.",
        "Tại {place}, điểm tập kết rác tạm thời nằm quá gần khu dân cư, gây mùi hôi khó chịu vào buổi chiều tối. Người dân đề nghị di dời hoặc bố trí thời gian thu gom hợp lý hơn.",
        "Sau giờ buôn bán, khu vực {place} thường xuyên còn lại nhiều rác thải, túi nilon và nước bẩn trên vỉa hè. Tình trạng này ảnh hưởng đến mỹ quan đô thị và vệ sinh môi trường. Đề nghị kiểm tra, nhắc nhở các hộ kinh doanh.",
        "Người dân tại {place} phản ánh nước thải từ một số cơ sở kinh doanh chảy trực tiếp ra đường, gây trơn trượt và mùi hôi. Đề nghị cơ quan chức năng kiểm tra hệ thống thoát nước và xử lý theo quy định.",
        "Tại {place}, rác sinh hoạt bị bỏ không đúng giờ thu gom, khiến khu vực thường xuyên mất vệ sinh. Đề nghị tăng cường tuyên truyền và có biện pháp xử lý các trường hợp vi phạm.",
        "Khu vực {place} có nhiều rác thải vương vãi sau mưa, gây tắc rãnh thoát nước và ảnh hưởng đến sinh hoạt của người dân. Kính đề nghị đơn vị phụ trách vệ sinh môi trường kiểm tra, dọn dẹp."
    
    ],
}


# =========================
# TẠO DỮ LIỆU ẢO
# =========================
current_counts = df["label"].value_counts().to_dict()
synthetic_rows = []

synthetic_id = 1

for label in labels_to_augment:
    current_count = current_counts.get(label, 0)
    need_count = max(0, TARGET_COUNT - current_count)

    templates = synthetic_templates[label]

    print(f"{label}: hiện có {current_count}, cần thêm {need_count}")

    for i in range(need_count):
        template = templates[i % len(templates)]
    
        # Dòng quan trọng: thay {place} bằng địa điểm ngẫu nhiên
        final_content = add_random_place(template)

        synthetic_rows.append({
            "id": f"SYN{synthetic_id:04d}",
            "city": "Hanoi",
            "time": "",
            "content": final_content,
            "clean_content": final_content,
            "compound_content": make_ml_text(final_content),
            "ml_text": make_ml_text(final_content),
            "handler": "",
            "status": "Dữ liệu ảo",
            "url": "",
            "label": label,
            "priority": "trung_binh",
            "is_synthetic": True
        })

        synthetic_id += 1

synthetic_df = pd.DataFrame(synthetic_rows)

# Thêm cột is_synthetic cho dữ liệu thật
df["is_synthetic"] = False

# Đảm bảo cùng cột
for col in df.columns:
    if col not in synthetic_df.columns:
        synthetic_df[col] = ""

for col in synthetic_df.columns:
    if col not in df.columns:
        df[col] = ""

synthetic_df = synthetic_df[df.columns]

# Gộp dữ liệu
final_df = pd.concat([df, synthetic_df], ignore_index=True)

# Lưu file
synthetic_df.to_csv(synthetic_output_path, index=False, encoding="utf-8-sig")
final_df.to_csv(combined_output_path, index=False, encoding="utf-8-sig")

print("\n==============================")
print("ĐÃ TẠO DỮ LIỆU ẢO")
print("File dữ liệu ảo:", synthetic_output_path)
print("File sau khi gộp:", combined_output_path)
print("==============================")

print("\nPhân bố label sau khi gộp:")
print(final_df["label"].value_counts())