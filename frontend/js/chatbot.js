const RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook";
const FASTAPI_URL = "http://127.0.0.1:8000";

window.VIETMAP_SERVICES_KEY = window.VIETMAP_SERVICES_KEY || "ed9c43c7c34836b71f11afe43e42e6103b1b2bf886421643";

let chatImagePath = null;
let chatMode = "";
let pendingReportLocation = null;
let waitingLocationConfirm = false;
let waitingImageChoice = false;
let CHAT_SENDER_ID = localStorage.getItem("chat_sender_id");

if (!CHAT_SENDER_ID) {
    CHAT_SENDER_ID = "web_user_" + Date.now();
    localStorage.setItem("chat_sender_id", CHAT_SENDER_ID);
}



let waitingFor = null;

function toggleChatbot() {
    const chatbotBox = document.getElementById("chatbotBox");
    chatbotBox.style.display = chatbotBox.style.display === "flex" ? "none" : "flex";
}
function askConfirmLocation(locationText) {
    pendingReportLocation = locationText;
    waitingLocationConfirm = true;

    const messages = document.getElementById("chatbotMessages");

    const box = document.createElement("div");
    box.classList.add("chat-message", "bot-message");

    box.innerHTML = `
        <div>Bạn xác nhận địa điểm phản ánh là:</div>
        <div 
            style="font-weight:600; color:#0d6efd; margin:8px 0; cursor:pointer;"
            onclick="confirmPendingLocation()"
        >
            📍 ${locationText}
        </div>
        <div style="font-size:13px; margin-bottom:8px;">
            Nếu đúng, bấm OK hoặc bấm vào địa chỉ. Nếu sai, hãy nhập lại địa chỉ mới.
        </div>
        <button 
            type="button"
            onclick="confirmPendingLocation()"
            style="border:none; background:#0d6efd; color:white; padding:6px 14px; border-radius:999px; cursor:pointer;"
        >
            OK
        </button>
    `;

    messages.appendChild(box);
    messages.scrollTop = messages.scrollHeight;
}
function confirmPendingLocation() {
    if (!pendingReportLocation) {
        addMessage("Chưa có địa điểm để xác nhận. Bạn vui lòng nhập lại địa điểm.", "bot");
        chatMode = "waiting_report_location";
        return;
    }

    waitingLocationConfirm = false;
    waitingImageChoice = true;

    addMessage("Bạn có muốn thêm ảnh minh chứng cho phản ánh này không? Nhập 'có' để thêm ảnh hoặc 'không' để bỏ qua.", "bot");
}
async function sendLocationAfterImageChoice() {
    if (!pendingReportLocation) {
        addMessage("Không tìm thấy địa điểm phản ánh. Bạn vui lòng nhập lại địa điểm.", "bot");
        chatMode = "waiting_report_location";
        return;
    }

    try {
        const botResponses = await sendMessageToRasa(pendingReportLocation);

        handleBotResponses(botResponses);

    } catch (error) {
        console.error(error);
        addMessage("Không thể gửi phản ánh. Bạn kiểm tra Rasa server hoặc backend nhé.", "bot");
    }
}
function addMessage(text, sender) {
    const messages = document.getElementById("chatbotMessages");

    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chat-message");

    if (sender === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("bot-message");
    }

    messageDiv.textContent = text;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

async function sendMessageToRasa(message) {
    const response = await fetch(RASA_API_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            sender: CHAT_SENDER_ID,
            message: message,
            metadata: {
                image_path: chatImagePath
            }
        })
    });

    if (!response.ok) {
        throw new Error("Không thể kết nối Rasa API");
    }

    return await response.json();
}

async function sendChatMessage() {
    const input = document.getElementById("chatbotInput");
    let userMessage = input.value.trim();

    if (!userMessage) return;

    addMessage(userMessage, "user");
    input.value = "";

    // Đang chờ xác nhận địa điểm
    if (waitingLocationConfirm) {
        const answer = userMessage.toLowerCase();

        if (
            answer === "ok" ||
            answer === "oke" ||
            answer === "đúng" ||
            answer === "dung" ||
            answer === "chính xác" ||
            answer === "xac nhan" ||
            answer === "xác nhận"
        ) {
            confirmPendingLocation();
            return;
        }

        // Nếu người dùng nhập lại địa chỉ mới
        pendingReportLocation = userMessage;
        askConfirmLocation(pendingReportLocation);
        return;
    }

    // Đang chờ chọn có thêm ảnh không
    if (waitingImageChoice) {
        const answer = userMessage.toLowerCase();

        if (
            answer.includes("không") ||
            answer.includes("ko") ||
            answer === "k" ||
            answer.includes("bỏ qua")
        ) {
            waitingImageChoice = false;
            await sendLocationAfterImageChoice();
            return;
        }

        if (
            answer.includes("có") ||
            answer === "co" ||
            answer.includes("thêm")
        ) {
            addMessage("Bạn hãy bấm nút 🖼️ Thêm ảnh để tải ảnh minh chứng lên.", "bot");
            chatMode = "waiting_image_upload";
            return;
        }

        addMessage("Bạn muốn thêm ảnh minh chứng không? Nhập 'có' để thêm ảnh hoặc 'không' để bỏ qua.", "bot");
        return;
    }

    // Rasa đang hỏi địa điểm phản ánh
    // Chỉ hỏi xác nhận, chưa gửi sang Rasa
    if (chatMode === "waiting_report_location") {
        askConfirmLocation(userMessage);
        return;
    }

    let messageToRasa = userMessage;

    if (chatMode === "report_code") {
        messageToRasa = "Kiểm tra phản ánh số " + userMessage;
        chatMode = "";
    } else if (chatMode === "report_location_lookup") {
        messageToRasa = "Kiểm tra phản ánh ở " + userMessage;
        chatMode = "";
    }

    try {
        const botResponses = await sendMessageToRasa(messageToRasa);
        handleBotResponses(botResponses);
    } catch (error) {
        console.error(error);
        addMessage("Không kết nối được chatbot. Bạn kiểm tra Rasa server đã chạy port 5005 chưa nhé.", "bot");
    }
}
function handleBotResponses(botResponses) {
    if (!botResponses || botResponses.length === 0) {
        addMessage("Tôi chưa hiểu ý bạn. Bạn có thể nhập lại rõ hơn không?", "bot");
        return;
    }

    botResponses.forEach(response => {
        if (response.text) {
            addMessage(response.text, "bot");

            if (response.text.includes("Vấn đề xảy ra ở đâu")) {
                chatMode = "waiting_report_location";
            }

            if (response.text.includes("Mã phản ánh")) {
                chatMode = "";
                pendingReportLocation = null;
                waitingLocationConfirm = false;
                waitingImageChoice = false;
                chatImagePath = null;

                const status = document.getElementById("chatImageStatus");
                if (status) status.textContent = "";
            }

            if (response.text.includes("Đã hủy gửi phản ánh")) {
                chatMode = "";
                pendingReportLocation = null;
                waitingLocationConfirm = false;
                waitingImageChoice = false;
                chatImagePath = null;
            }
        }

        if (response.image) {
            addImageMessage(response.image, "bot");
        }
    });
}
function sendSuggestion(text) {
    waitingFor = null;

    const input = document.getElementById("chatbotInput");
    input.value = text;
    sendChatMessage();
}

function askReportCode() {
    waitingFor = "report_code";
    addMessage("Bạn muốn tra cứu mã phản ánh nào? Vui lòng nhập mã, ví dụ: 17", "bot");
}

function askReportLocation() {
    waitingFor = "report_location_lookup";
    addMessage("Bạn muốn tra cứu phản ánh ở địa điểm nào? Vui lòng nhập địa điểm, ví dụ: trước cổng trường VKU", "bot");
}

document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("chatbotInput");

    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            sendChatMessage();
        }
    });
});

async function handleChatImageUpload(event) {
    const file = event.target.files[0];
    const status = document.getElementById("chatImageStatus");

    if (!file) return;

    const formData = new FormData();
    formData.append("image", file);

    status.textContent = "Đang tải ảnh lên...";

    try {
        const response = await fetch(`${FASTAPI_URL}/upload-chat-image`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Upload ảnh thất bại");
        }

        const data = await response.json();
        chatImagePath = data.image_path;

        status.textContent = "Đã thêm ảnh minh chứng.";
        addMessage("Đã thêm ảnh minh chứng.", "bot");

        const imageUrl = `${FASTAPI_URL}${data.image_path}`;
        addImageMessage(imageUrl, "bot");

        // Nếu đang chờ ảnh trong luồng gửi phản ánh thì lưu phản ánh luôn
        if (chatMode === "waiting_image_upload" && pendingReportLocation) {
            chatMode = "";
            waitingImageChoice = false;

            await sendLocationAfterImageChoice();
        }

    } catch (error) {
        console.error(error);
        status.textContent = "Không thể tải ảnh lên.";
        addMessage("Không thể tải ảnh lên. Bạn thử lại sau nhé.", "bot");
    }
}
async function sendCurrentLocationToChat() {
    if (chatMode !== "waiting_report_location") {
        addMessage("Bạn hãy bấm 'Gửi phản ánh' và nhập nội dung trước. Khi bot hỏi địa điểm, bạn có thể bấm 📍 Gửi vị trí.", "bot");
        return;
    }

    if (!navigator.geolocation) {
        addMessage("Trình duyệt không hỗ trợ lấy vị trí.", "bot");
        return;
    }

    addMessage("Đang lấy vị trí hiện tại...", "bot");

    navigator.geolocation.getCurrentPosition(
        async function (position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            try {
                const address = await reverseGeocodeVietmapForChat(lat, lng);
                const locationText = address || `${lat}, ${lng}`;

                addMessage(locationText, "user");

                // Chỉ hỏi xác nhận địa điểm, chưa lưu database
                askConfirmLocation(locationText);

            } catch (error) {
                console.error(error);
                addMessage("Không thể lấy địa chỉ từ Vietmap. Bạn vui lòng nhập địa điểm thủ công.", "bot");
            }
        },
        function (error) {
            console.error(error);
            addMessage("Bạn cần cho phép trình duyệt truy cập vị trí để dùng chức năng này.", "bot");
        },
        {
            enableHighAccuracy: true,
            timeout: 30000,
            maximumAge: 0
        }
    );
}
function addImageMessage(imageUrl, sender) {
    const messages = document.getElementById("chatbotMessages");

    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chat-message");

    if (sender === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("bot-message");
    }

    const img = document.createElement("img");
    img.src = imageUrl;
    img.alt = "Ảnh minh chứng";
    img.style.maxWidth = "100%";
    img.style.borderRadius = "10px";
    img.style.marginTop = "6px";
    img.style.cursor = "pointer";

    img.onclick = function () {
        window.open(imageUrl, "_blank");
    };

    messageDiv.appendChild(img);
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}
async function reverseGeocodeVietmapForChat(lat, lng) {
    const url = `https://maps.vietmap.vn/api/reverse/v3?apikey=${window.VIETMAP_SERVICES_KEY}&lat=${lat}&lng=${lng}`;

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error("Không gọi được Vietmap API");
    }

    const data = await response.json();
    console.log("Vietmap chat reverse data:", data);

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