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
    return `<img src="http://127.0.0.1:8000${report.image_path}" alt="${report.title}" />`;
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
    const response = await fetch(`http://127.0.0.1:8000/reports/${type}`);

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
    const response = await fetch(`http://127.0.0.1:8000/report/${id}`);

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
        <p>Hãy kiểm tra FastAPI đã chạy tại <code>http://127.0.0.1:8000</code> chưa.</p>
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
      const response = await fetch("http://127.0.0.1:8000/predict", {
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

const VIETMAP_TILEMAP_KEY = "d1a19a1564c885dd9cc8dd5916f9f4b6b8b5ae9b25a16a41";
const VIETMAP_SERVICES_KEY = "ed9c43c7c34836b71f11afe43e42e6103b1b2bf886421643";

let reportMap = null;
let reportMarker = null;

async function getCurrentLocationForReport() {
    const locationInput = document.getElementById("reportLocation");
    const statusElement = document.getElementById("locationStatus");
    const latInput = document.getElementById("reportLatitude");
    const lngInput = document.getElementById("reportLongitude");

    if (!navigator.geolocation) {
        statusElement.textContent = "Trình duyệt không hỗ trợ lấy vị trí.";
        return;
    }

    statusElement.textContent = "Đang lấy vị trí hiện tại...";

    navigator.geolocation.getCurrentPosition(
        async function (position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            if (latInput) latInput.value = lat;
            if (lngInput) lngInput.value = lng;

            showReportMap(lat, lng);

            statusElement.textContent = "Đang chuyển tọa độ thành địa chỉ...";

            try {
                const address = await reverseGeocodeVietmap(lat, lng);

                if (address) {
                    locationInput.value = address;
                    statusElement.textContent = "Đã lấy địa điểm thành công.";
                } else {
                    locationInput.value = `${lat}, ${lng}`;
                    statusElement.textContent = "Không tìm thấy địa chỉ, đã điền tọa độ.";
                }
            } catch (error) {
                console.error("Lỗi Vietmap:", error);
                locationInput.value = `${lat}, ${lng}`;
                statusElement.textContent = "Không thể lấy địa chỉ từ Vietmap, đã điền tọa độ.";
            }
        },
        function (error) {
            console.error("GPS Error:", error);

            if (error.code === error.PERMISSION_DENIED) {
                statusElement.textContent = "Bạn cần cho phép trình duyệt truy cập vị trí.";
            } else if (error.code === error.TIMEOUT) {
                statusElement.textContent = "Lấy vị trí quá lâu, vui lòng thử lại.";
            } else {
                statusElement.textContent = "Không thể lấy vị trí hiện tại.";
            }
        },
        {
            enableHighAccuracy: true,
            timeout: 30000,
            maximumAge: 0
        }
    );
}

function showReportMap(lat, lng) {
    if (typeof vietmapgl === "undefined") {
        console.error("Vietmap GL chưa được load. Kiểm tra lại script Vietmap trong HTML.");
        document.getElementById("locationStatus").textContent =
            "Chưa tải được thư viện bản đồ Vietmap.";
        return;
    }

    const mapDiv = document.getElementById("reportMap");
    mapDiv.style.display = "block";

    if (!reportMap) {
        vietmapgl.accessToken = VIETMAP_TILEMAP_KEY;

        reportMap = new vietmapgl.Map({
            container: "reportMap",
            style: `https://maps.vietmap.vn/api/maps/light/styles.json?apikey=${VIETMAP_TILEMAP_KEY}`,
            center: [lng, lat],
            zoom: 16
        });

        reportMap.addControl(new vietmapgl.NavigationControl(), "top-right");
    } else {
        reportMap.setCenter([lng, lat]);
        reportMap.setZoom(16);
    }

    if (reportMarker) {
        reportMarker.remove();
    }

    reportMarker = new vietmapgl.Marker()
        .setLngLat([lng, lat])
        .addTo(reportMap);

    setTimeout(() => {
        reportMap.resize();
    }, 300);
}

async function reverseGeocodeVietmap(lat, lng) {
    const url = `https://maps.vietmap.vn/api/reverse/v3?apikey=${VIETMAP_SERVICES_KEY}&lat=${lat}&lng=${lng}`;

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error("Không gọi được Vietmap Reverse API");
    }

    const data = await response.json();
    console.log("Vietmap reverse data:", data);

    const actualData = Array.isArray(data) ? data[0] : data;

    if (actualData && actualData.display) {
        return actualData.display;
    }

    if (actualData && actualData.address) {
        return actualData.address;
    }

    if (actualData && actualData.name) {
        return actualData.name;
    }

    return null;
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
    const response = await fetch("http://127.0.0.1:8000/predict", {
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







let allSearchReports = [];

async function loadSearchReportsPage() {
  const searchReportList = document.getElementById("searchReportList");
  const resultCount = document.getElementById("resultCount");

  if (!searchReportList || !resultCount) {
    return;
  }

  searchReportList.innerHTML = `
    <div class="col-12">
      <div class="empty-box">
        <h4>Đang tải dữ liệu...</h4>
        <p>Vui lòng chờ trong giây lát.</p>
      </div>
    </div>
  `;

  try {
    const response = await fetch("http://127.0.0.1:8000/reports");

    if (!response.ok) {
      throw new Error("Không lấy được danh sách phản ánh.");
    }

    allSearchReports = await response.json();

    renderSearchReports(allSearchReports);
  } catch (error) {
    searchReportList.innerHTML = `
      <div class="col-12">
        <div class="empty-box">
          <h4>Không kết nối được backend</h4>
          <p>Hãy kiểm tra FastAPI đã chạy tại <code>http://127.0.0.1:8000</code> chưa.</p>
        </div>
      </div>
    `;

    resultCount.textContent = "Không thể tải dữ liệu.";
    console.error(error);
  }
}


function renderSearchReports(reports) {
  const searchReportList = document.getElementById("searchReportList");
  const resultCount = document.getElementById("resultCount");

  if (!searchReportList || !resultCount) {
    return;
  }

  resultCount.textContent = `Tìm thấy ${reports.length} phản ánh.`;

  if (reports.length === 0) {
    searchReportList.innerHTML = `
      <div class="col-12">
        <div class="empty-box">
          <h4>Không có kết quả phù hợp</h4>
          <p>Thử thay đổi từ khóa, địa chỉ hoặc phân loại khác.</p>
        </div>
      </div>
    `;
    return;
  }

  searchReportList.innerHTML = reports
    .map(
        (report) => `
        <div class="col-md-6 col-xl-4">
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
}

function filterReports() {
  const locationKeyword = document
    .getElementById("searchLocation")
    .value
    .trim()
    .toLowerCase();

  const contentKeyword = document
    .getElementById("searchContent")
    .value
    .trim()
    .toLowerCase();

  const categoryValue = document
    .getElementById("searchCategory")
    .value;

  const timeFilter = document.getElementById("timeFilter").value;
  const startDateValue = document.getElementById("startDate").value;
  const endDateValue = document.getElementById("endDate").value;

  if (timeFilter === "custom" && (!startDateValue || !endDateValue)) {
    alert("Vui lòng chọn ngày bắt đầu và ngày kết thúc.");
    return;
  }

  const filtered = allSearchReports.filter((report) => {
    const location = (report.location || "").toLowerCase();
    const title = (report.title || "").toLowerCase();
    const content = (report.content || "").toLowerCase();

    const locationMatch = location.includes(locationKeyword);

    const contentText = `${title} ${content}`;
    const contentMatch = contentText.includes(contentKeyword);

    const categoryMatch = categoryValue
      ? report.predicted_category === categoryValue
      : true;

    const timeMatch = checkTimeMatch(
      report.created_at,
      timeFilter,
      startDateValue,
      endDateValue
    );

    return locationMatch && contentMatch && categoryMatch && timeMatch;
  });

  renderSearchReports(filtered);
}
function checkTimeMatch(createdAt, timeFilter, startDateValue, endDateValue) {
  if (timeFilter === "all") {
    return true;
  }

  if (!createdAt) {
    return false;
  }

  const reportDate = new Date(createdAt);
  const now = new Date();

  const todayStart = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate(),
    0,
    0,
    0
  );

  const tomorrowStart = new Date(todayStart);
  tomorrowStart.setDate(todayStart.getDate() + 1);

  if (timeFilter === "today") {
    return reportDate >= todayStart && reportDate < tomorrowStart;
  }

  if (timeFilter === "7days") {
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(now.getDate() - 7);

    return reportDate >= sevenDaysAgo && reportDate <= now;
  }

  if (timeFilter === "30days") {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(now.getDate() - 30);

    return reportDate >= thirtyDaysAgo && reportDate <= now;
  }

  if (timeFilter === "custom") {
    const startDate = new Date(startDateValue);
    const endDate = new Date(endDateValue);

    startDate.setHours(0, 0, 0, 0);
    endDate.setHours(23, 59, 59, 999);

    return reportDate >= startDate && reportDate <= endDate;
  }

  return true;
}
function resetSearchReports() {
  document.getElementById("searchLocation").value = "";
  document.getElementById("searchContent").value = "";
  document.getElementById("searchCategory").value = "";
  document.getElementById("timeFilter").value = "all";
  document.getElementById("startDate").value = "";
  document.getElementById("endDate").value = "";
  document.getElementById("customDateBox").style.display = "none";

  renderSearchReports(allSearchReports);
}

loadSearchReportsPage();

function handleTimeFilterChange() {
  const timeFilter = document.getElementById("timeFilter");
  const customDateBox = document.getElementById("customDateBox");
  const startDate = document.getElementById("startDate");
  const endDate = document.getElementById("endDate");

  if (timeFilter.value === "custom") {
    customDateBox.style.display = "flex";
  } else {
    customDateBox.style.display = "none";
    startDate.value = "";
    endDate.value = "";
  }
}
