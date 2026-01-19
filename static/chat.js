function startChat(alias, roomName) {
    const ws = new WebSocket(`ws://${window.location.host}/ws/${roomName}?alias=${alias}`);
    const input = document.getElementById("message-input-sample");
    const chatWindow = document.getElementById("chat-window");
    const sendBtn = document.getElementById("send-btn");

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const msgDiv = document.createElement("div");

        // Use 'right' for current user, 'left' for others
        msgDiv.className = data.alias === alias ? "bubble right" : "bubble left";
        msgDiv.textContent = data.message;
        
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    function sendMsg() {
        if (input.value.trim() !== "" && ws.readyState === WebSocket.OPEN) {
            ws.send(input.value);
            input.value = "";
        }
    }

    sendBtn.onclick = sendMsg;
    input.onkeypress = (e) => { if(e.key === "Enter") sendMsg(); };
}