const RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook";
const CHAT_SENDER_ID = "web_user_" + Date.now();

let waitingFor = null;

function toggleChatbot() {
    const chatbotBox = document.getElementById("chatbotBox");
    chatbotBox.style.display = chatbotBox.style.display === "flex" ? "none" : "flex";
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
            message: message
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

    // Hiển thị đúng nội dung người dùng nhập
    addMessage(userMessage, "user");
    input.value = "";

    // Tin nhắn thật sự gửi sang Rasa
    let messageToRasa = userMessage;

    if (waitingFor === "report_code") {
        messageToRasa = "Kiểm tra phản ánh số " + userMessage;
        waitingFor = null;
    } else if (waitingFor === "report_location_lookup") {
        messageToRasa = "Kiểm tra phản ánh ở " + userMessage;
        waitingFor = null;
    }

    console.log("Gửi sang Rasa:", messageToRasa);

    try {
        const botResponses = await sendMessageToRasa(messageToRasa);

        if (botResponses.length === 0) {
            addMessage("Tôi chưa hiểu ý bạn. Bạn có thể nhập lại rõ hơn không?", "bot");
            return;
        }

        botResponses.forEach(response => {
            if (response.text) {
                addMessage(response.text, "bot");
            }
        });

    } catch (error) {
        console.error(error);
        addMessage("Không kết nối được chatbot. Bạn kiểm tra Rasa server đã chạy port 5005 chưa nhé.", "bot");
    }
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