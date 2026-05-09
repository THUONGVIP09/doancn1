const categoryNames = {
  duong_cau_ha_tang_hu_hong: "Đường, cầu, hạ tầng hư hỏng",
  dien_luc_chieu_sang: "Điện lực, chiếu sáng",
  cong_ho_ga_thoat_nuoc: "Cống, hố ga, thoát nước",
  via_he_long_duong: "Vỉa hè, lòng đường",
  cay_xanh_vat_can: "Cây xanh, vật cản",
  bien_bao: "Biển báo",
  to_chuc_giao_thong: "Tổ chức giao thông",
  den_tin_hieu: "Đèn tín hiệu",
  rac_thai_ve_sinh_moi_truong: "Rác thải, vệ sinh môi trường",
  do_xe_can_tro: "Đỗ xe cản trở",
  khac: "Khác"
};

const reports = [
  {
    id: 1,
    type: "duong_cau_ha_tang_hu_hong",
    title: "Mặt đường xuất hiện ổ gà lớn",
    location: "Đường Nguyễn Văn Linh, Đà Nẵng",
    description: "Mặt đường bị bong tróc, xuất hiện ổ gà gây nguy hiểm cho người tham gia giao thông.",
    status: "Chờ xử lý",
    icon: "🛣️"
  },
  {
    id: 2,
    type: "duong_cau_ha_tang_hu_hong",
    title: "Nắp bê tông trên cầu bị nứt",
    location: "Khu vực cầu Rồng",
    description: "Một vị trí trên cầu có dấu hiệu hư hỏng, cần được kiểm tra và sửa chữa.",
    status: "Đang xử lý",
    icon: "🌉"
  },
  {
    id: 3,
    type: "dien_luc_chieu_sang",
    title: "Đèn đường không hoạt động",
    location: "Đường Lê Duẩn, Hải Châu",
    description: "Một số bóng đèn chiếu sáng công cộng bị tắt vào ban đêm.",
    status: "Chờ xử lý",
    icon: "💡"
  },
  {
    id: 4,
    type: "cong_ho_ga_thoat_nuoc",
    title: "Hố ga bị mất nắp",
    location: "Đường Trần Cao Vân",
    description: "Hố ga trên lề đường bị mất nắp, có nguy cơ gây tai nạn cho người dân.",
    status: "Đang xử lý",
    icon: "🕳️"
  },
  {
    id: 5,
    type: "via_he_long_duong",
    title: "Vỉa hè bị lấn chiếm",
    location: "Khu vực chợ Cồn",
    description: "Một số hộ kinh doanh đặt vật dụng trên vỉa hè, ảnh hưởng đến người đi bộ.",
    status: "Chờ xử lý",
    icon: "🚶"
  },
  {
    id: 6,
    type: "cay_xanh_vat_can",
    title: "Cành cây che khuất tầm nhìn",
    location: "Đường Điện Biên Phủ",
    description: "Cành cây mọc thấp, che khuất biển báo và gây khó quan sát.",
    status: "Đã xử lý",
    icon: "🌳"
  },
  {
    id: 7,
    type: "bien_bao",
    title: "Biển báo bị nghiêng",
    location: "Ngã tư Nguyễn Tri Phương",
    description: "Biển báo giao thông bị lệch, khó quan sát từ xa.",
    status: "Chờ xử lý",
    icon: "🚧"
  },
  {
    id: 8,
    type: "to_chuc_giao_thong",
    title: "Phân luồng giao thông chưa hợp lý",
    location: "Khu vực vòng xoay phía Tây",
    description: "Lưu lượng phương tiện đông, thường xuyên xảy ra ùn ứ vào giờ cao điểm.",
    status: "Đang xử lý",
    icon: "🚗"
  },
  {
    id: 9,
    type: "den_tin_hieu",
    title: "Đèn tín hiệu bị lỗi",
    location: "Ngã tư Ông Ích Khiêm",
    description: "Đèn tín hiệu chuyển trạng thái không ổn định, gây khó khăn cho phương tiện.",
    status: "Chờ xử lý",
    icon: "🚦"
  },
  {
    id: 10,
    type: "rac_thai_ve_sinh_moi_truong",
    title: "Rác thải tồn đọng ven đường",
    location: "Khu dân cư Hòa Khánh",
    description: "Rác thải sinh hoạt chưa được thu gom, gây mất mỹ quan đô thị.",
    status: "Đang xử lý",
    icon: "🗑️"
  },
  {
    id: 11,
    type: "do_xe_can_tro",
    title: "Xe ô tô đỗ chắn lối đi",
    location: "Đường Phan Châu Trinh",
    description: "Xe đỗ sai quy định, cản trở lối đi và ảnh hưởng đến giao thông.",
    status: "Chờ xử lý",
    icon: "🅿️"
  },
  {
    id: 12,
    type: "khac",
    title: "Phản ánh khác cần kiểm tra",
    location: "Khu vực trung tâm thành phố",
    description: "Nội dung phản ánh chưa thuộc nhóm cụ thể, cần cán bộ kiểm tra thêm.",
    status: "Chờ xử lý",
    icon: "📌"
  }
];

function getStatusClass(status) {
  if (status === "Đang xử lý") return "status-processing";
  if (status === "Đã xử lý") return "status-done";
  return "status-pending";
}
function getReportIcon(category) {
  const icons = {
    duong_cau_ha_tang_hu_hong: "🛣️",
    dien_luc_chieu_sang: "💡",
    cong_ho_ga_thoat_nuoc: "🕳️",
    via_he_long_duong: "🚶",
    cay_xanh_vat_can: "🌳",
    bien_bao: "🚧",
    to_chuc_giao_thong: "🚗",
    den_tin_hieu: "🚦",
    rac_thai_ve_sinh_moi_truong: "🗑️",
    do_xe_can_tro: "🅿️",
    khac: "📌"
  };

  return icons[category] || "📌";
}
function renderReportImage(report) {
  if (report.image_path) {
    return `<img src="http://127.0.0.1:8001${report.image_path}" alt="${report.title}" />`;
  }

  return getReportIcon(report.predicted_category);
}

async function renderCategoryPage() {
  const reportList = document.getElementById("reportList");
  const categoryTitle = document.getElementById("categoryTitle");
  const categoryDesc = document.getElementById("categoryDesc");

  if (!reportList || !categoryTitle || !categoryDesc) {
    return;
  }

  const urlParams = new URLSearchParams(window.location.search);
  const type = urlParams.get("type");

  const categoryName = categoryNames[type] || "Danh mục phản ánh";

  categoryTitle.textContent = categoryName;
  categoryDesc.textContent = `Danh sách các phản ánh thuộc nhóm: ${categoryName}.`;

  reportList.innerHTML = `
    <div class="col-12">
      <div class="empty-box">
        <h4>Đang tải dữ liệu...</h4>
        <p>Vui lòng chờ trong giây lát.</p>
      </div>
    </div>
  `;

  try {
    const response = await fetch(`http://127.0.0.1:8001/reports/${type}`);

    if (!response.ok) {
      throw new Error("Không lấy được dữ liệu từ backend.");
    }

    const filteredReports = await response.json();

    if (filteredReports.length === 0) {
      reportList.innerHTML = `
        <div class="col-12">
          <div class="empty-box">
            <h4>Chưa có phản ánh nào</h4>
            <p>Danh mục này hiện chưa có phản ánh được gửi lên.</p>
          </div>
        </div>
      `;
      return;
    }

    reportList.innerHTML = filteredReports
      .map(
        (report) => `
          <div class="col-md-6 col-lg-4">
            <a href="detail.html?id=${report.id}" class="report-link">
              <div class="report-card">
                <div class="report-img">
                  ${renderReportImage(report)}
                </div>

                <div class="report-body">
                  <h5>${report.title}</h5>

                  <div class="report-meta">
                    📍 ${report.location}
                  </div>

                  <p>${report.content}</p>

                  <span class="status-badge ${getStatusClass(report.status)}">
                    ${report.status}
                  </span>
                </div>
              </div>
            </a>
          </div>
        `
      )
      .join("");
  } catch (error) {
    reportList.innerHTML = `
      <div class="col-12">
        <div class="empty-box">
          <h4>Không kết nối được backend</h4>
          <p>Hãy kiểm tra FastAPI đã chạy tại <code>http://127.0.0.1:8001</code> chưa.</p>
        </div>
      </div>
    `;

    console.error(error);
  }
}

renderCategoryPage();














async function renderDetailPage() {
  const detailContent = document.getElementById("detailContent");

  if (!detailContent) {
    return;
  }

  const urlParams = new URLSearchParams(window.location.search);
  const id = Number(urlParams.get("id"));

  detailContent.innerHTML = `
    <div class="empty-box">
      <h4>Đang tải dữ liệu...</h4>
      <p>Vui lòng chờ trong giây lát.</p>
    </div>
  `;

  try {
    const response = await fetch(`http://127.0.0.1:8001/report/${id}`);

    if (!response.ok) {
      throw new Error("Không lấy được dữ liệu chi tiết.");
    }

    const report = await response.json();

    if (report.error) {
      detailContent.innerHTML = `
        <div class="empty-box">
          <h4>Không tìm thấy phản ánh</h4>
          <p>Dữ liệu phản ánh không tồn tại hoặc đã bị xóa.</p>
        </div>
      `;
      return;
    }

    const categoryName = report.predicted_name || categoryNames[report.predicted_category] || "Khác";

    detailContent.innerHTML = `
      <div class="detail-card">
        <div class="detail-image">
          ${renderReportImage(report)}
        </div>

        <div class="detail-body">
          <div class="detail-top">
            <span class="detail-category">${categoryName}</span>

            <span class="status-badge ${getStatusClass(report.status)}">
              ${report.status}
            </span>
          </div>

          <h1>${report.title}</h1>

          <div class="detail-info">
            <p><strong>📍 Vị trí:</strong> ${report.location}</p>
            <p><strong>🏷️ Mã nhãn:</strong> ${report.predicted_category}</p>
            <p><strong>📊 Độ tin cậy:</strong> ${
                report.confidence ? (report.confidence * 100).toFixed(2) : "0.00"
                }%</p>
            <p><strong>🖼️ Ảnh:</strong> ${report.image_path || "Chưa có ảnh"}</p>
          </div>

          <div class="detail-description">
            <h5>Nội dung phản ánh</h5>
            <p>${report.content}</p>
          </div>

          <div class="detail-processing">
            <h5>Ghi chú xử lý</h5>
            <p>
              Phản ánh đã được hệ thống tiếp nhận và phân loại tự động.
              Cơ quan phụ trách sẽ kiểm tra hiện trường và cập nhật trạng thái xử lý.
            </p>
          </div>
        </div>
      </div>
    `;
  } catch (error) {
    detailContent.innerHTML = `
      <div class="empty-box">
        <h4>Không kết nối được backend</h4>
        <p>Hãy kiểm tra FastAPI đã chạy tại <code>http://127.0.0.1:8001</code> chưa.</p>
      </div>
    `;

    console.error(error);
  }
}

renderDetailPage();




async function handleReportForm() {
  const reportForm = document.getElementById("reportForm");
  const reportImage = document.getElementById("reportImage");
  const previewBox = document.getElementById("previewBox");
  const previewImage = document.getElementById("previewImage");
  const resultBox = document.getElementById("resultBox");
  const resultText = document.getElementById("resultText");

  if (!reportForm) {
    return;
  }

  if (reportImage) {
    reportImage.addEventListener("change", function () {
      const file = reportImage.files[0];

      if (!file) {
        previewBox.classList.add("d-none");
        previewImage.src = "";
        return;
      }

      const imageUrl = URL.createObjectURL(file);
      previewImage.src = imageUrl;
      previewBox.classList.remove("d-none");
    });
  }

  reportForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    event.stopPropagation();

    const title = document.getElementById("reportTitle").value.trim();
    const content = document.getElementById("reportContent").value.trim();
    const location = document.getElementById("reportLocation").value.trim();
    const imageFile = reportImage && reportImage.files.length > 0
      ? reportImage.files[0]
      : null;

    if (!title || !content || !location) {
      resultBox.classList.remove("d-none");
      resultText.innerHTML = "Vui lòng nhập đầy đủ tiêu đề, nội dung và vị trí.";
      return false;
    }

    const formData = new FormData();
    formData.append("title", title);
    formData.append("content", content);
    formData.append("location", location);

    if (imageFile) {
      formData.append("image", imageFile);
    }

    resultBox.classList.remove("d-none");
    resultText.innerHTML = "Đang gửi phản ánh và phân loại...";

    try {
      const response = await fetch("http://127.0.0.1:8001/predict", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText);
      }

      const data = await response.json();

      resultText.innerHTML = `
        <strong>Tiêu đề:</strong> ${data.title}<br>
        <strong>Vị trí:</strong> ${data.location}<br>
        <strong>Trạng thái:</strong> ${data.status}<br>
        <strong>Danh mục dự đoán:</strong> ${data.predicted_name}<br>
        <strong>Mã nhãn:</strong> ${data.predicted_category}<br>
        <strong>Độ tin cậy:</strong> ${formatConfidence(data.confidence)}%
      `;
    } catch (error) {
      resultText.innerHTML = `
        <strong>Lỗi:</strong> Không gửi được phản ánh.<br>
        Kiểm tra backend FastAPI và ảnh upload.<br>
        <code>${error.message}</code>
      `;

      console.error("Submit error:", error);
    }

    return false;
  });
}

//handleReportForm();

function formatConfidence(confidence) {
  const value = Number(confidence);

  if (Number.isNaN(value)) {
    return "0.00";
  }

  return (value * 100).toFixed(2);
}
async function submitReport() {
  const reportImage = document.getElementById("reportImage");
  const resultBox = document.getElementById("resultBox");
  const resultText = document.getElementById("resultText");

  const title = document.getElementById("reportTitle").value.trim();
  const content = document.getElementById("reportContent").value.trim();
  const location = document.getElementById("reportLocation").value.trim();

  const imageFile = reportImage && reportImage.files.length > 0
    ? reportImage.files[0]
    : null;

  if (!title || !content || !location) {
    resultBox.classList.remove("d-none");
    resultText.innerHTML = "Vui lòng nhập đầy đủ tiêu đề, nội dung và vị trí.";
    return;
  }

  const formData = new FormData();
  formData.append("title", title);
  formData.append("content", content);
  formData.append("location", location);

  if (imageFile) {
    formData.append("image", imageFile);
  }

  resultBox.classList.remove("d-none");
  resultText.innerHTML = "Đang gửi phản ánh và phân loại...";

  try {
    const response = await fetch("http://127.0.0.1:8001/predict", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText);
    }

    const data = await response.json();

    resultText.innerHTML = `
      <strong>Tiêu đề:</strong> ${data.title}<br>
      <strong>Vị trí:</strong> ${data.location}<br>
      <strong>Trạng thái:</strong> ${data.status}<br>
      <strong>Danh mục dự đoán:</strong> ${data.predicted_name}<br>
      <strong>Mã nhãn:</strong> ${data.predicted_category}<br>
      <strong>Độ tin cậy:</strong> ${formatConfidence(data.confidence)}%
    `;
  } catch (error) {
    resultText.innerHTML = `
      <strong>Lỗi:</strong> Không gửi được phản ánh.<br>
      <code>${error.message}</code>
    `;

    console.error("Submit error:", error);
  }
}