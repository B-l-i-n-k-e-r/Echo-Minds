document.addEventListener("DOMContentLoaded", () => {

    function startChat(alias, roomName) {
        const input = document.getElementById("message-input-sample");
        const chatWindow = document.getElementById("chat-window");
        const sendBtn = document.getElementById("send-btn");

        // Choose ws or wss depending on protocol
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const ws = new WebSocket(`${protocol}://${window.location.host}/ws/${roomName}?alias=${alias}`);

        // Handle incoming messages
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            const msgDiv = document.createElement("div");

            // Right for current user, left for others
            msgDiv.className = data.alias === alias ? "bubble right" : "bubble left";
            msgDiv.textContent = data.message;

            chatWindow.appendChild(msgDiv);
            chatWindow.scrollTop = chatWindow.scrollHeight;
        };

        // Send message function
        function sendMsg() {
            const message = input.value.trim();
            if (message !== "" && ws.readyState === WebSocket.OPEN) {
                ws.send(message);
                input.value = "";
            }
        }

        // Send button click
        sendBtn.addEventListener("click", sendMsg);

        // Press Enter to send
        input.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendMsg();
        });

        // Optional: alert user if disconnected (e.g., room deleted)
        ws.onclose = () => {
            const msgDiv = document.createElement("div");
            msgDiv.className = "bubble system";
            msgDiv.textContent = "You have been disconnected (room closed or left).";
            chatWindow.appendChild(msgDiv);
            chatWindow.scrollTop = chatWindow.scrollHeight;
            input.disabled = true;
            sendBtn.disabled = true;
        };
    }

    // Expose globally so HTML can call startChat()
    window.startChat = startChat;

});
