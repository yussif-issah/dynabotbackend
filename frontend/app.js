// Chat bot logic for /chat/{user_id}
if (window.CHAT_USER_ID) {

  console.log("Chat user ID:", window.CHAT_USER_ID);
  // Inject modern styles
  const style = document.createElement("style");
  style.innerHTML = `
    body {
      background: linear-gradient(135deg, #0f172a, #1e293b);
      font-family: 'Inter', sans-serif;
    }

    .chat-wrapper {
      width: 420px;
      height: 650px;
      margin: 60px auto;
      display: flex;
      flex-direction: column;
      background: rgba(255,255,255,0.06);
      backdrop-filter: blur(20px);
      border-radius: 24px;
      box-shadow: 0 25px 50px rgba(0,0,0,0.4);
      border: 1px solid rgba(255,255,255,0.1);
      overflow: hidden;
      animation: fadeIn 0.4s ease;
    }

    .chat-header {
      padding: 20px;
      background: rgba(255,255,255,0.05);
      color: white;
      font-weight: 600;
      border-bottom: 1px solid rgba(255,255,255,0.08);
    }

    .chat-header small {
      opacity: 0.6;
      font-weight: 400;
    }

    .chat-messages {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .message {
      max-width: 75%;
      padding: 12px 16px;
      border-radius: 16px;
      font-size: 14px;
      line-height: 1.5;
      animation: slideUp 0.25s ease;
    }

    .user {
      align-self: flex-end;
      background: linear-gradient(135deg, #6366f1, #8b5cf6);
      color: white;
      border-bottom-right-radius: 6px;
    }

    .bot {
      background: rgba(255,255,255,0.08);
      color: white;
      border-bottom-left-radius: 6px;
    }

    .chat-input-area {
      padding: 16px;
      background: rgba(255,255,255,0.05);
      border-top: 1px solid rgba(255,255,255,0.08);
      display: flex;
      gap: 10px;
    }

    .chat-input-area input {
      flex: 1;
      padding: 12px 14px;
      border-radius: 14px;
      border: none;
      outline: none;
      background: rgba(255,255,255,0.1);
      color: white;
      font-size: 14px;
    }

    .chat-input-area input::placeholder {
      color: rgba(255,255,255,0.5);
    }

    .chat-input-area button {
      padding: 12px 18px;
      border-radius: 14px;
      border: none;
      cursor: pointer;
      font-weight: 500;
      color: white;
      background: linear-gradient(135deg, #6366f1, #8b5cf6);
      transition: 0.2s ease;
    }

    .chat-input-area button:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(99,102,241,0.4);
    }

    .typing span {
      width: 6px;
      height: 6px;
      background: white;
      border-radius: 50%;
      display: inline-block;
      margin-right: 4px;
      animation: blink 1.4s infinite both;
    }

    .typing span:nth-child(2) { animation-delay: .2s; }
    .typing span:nth-child(3) { animation-delay: .4s; }

    @keyframes blink {
      0% { opacity: 0.2; }
      20% { opacity: 1; }
      100% { opacity: 0.2; }
    }

    @keyframes slideUp {
      from { transform: translateY(10px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: scale(0.97); }
      to { opacity: 1; transform: scale(1); }
    }
  `;
  document.head.appendChild(style);

  // Build chat UI
  const chat = document.createElement("div");
  chat.className = "chat-wrapper";
  chat.innerHTML = `
    <div class="chat-header">
      Dynabot <br>
      <small>User: ${window.CHAT_USER_ID} • Online</small>
    </div>
    <div class="chat-messages" id="chatMessages"></div>
    <div class="chat-input-area">
      <input id="chatInput" type="text" placeholder="Type your message..." />
      <button id="chatSendBtn">Send</button>
    </div>
  `;
  document.body.prepend(chat);

  const chatMessages = document.getElementById("chatMessages");
  const chatInput = document.getElementById("chatInput");
  const chatSendBtn = document.getElementById("chatSendBtn");

  function appendMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = `message ${sender}`;
    msg.innerText = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function showTyping() {
    const typing = document.createElement("div");
    typing.className = "message bot";
    typing.id = "typing";
    typing.innerHTML = `
      <div class="typing">
        <span></span><span></span><span></span>
      </div>
    `;
    chatMessages.appendChild(typing);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function removeTyping() {
    const typing = document.getElementById("typing");
    if (typing) typing.remove();
  }

  async function sendMessage() {
    const msg = chatInput.value.trim();
    if (!msg) return;

    appendMessage(msg, "user");
    chatInput.value = "";
    showTyping();

    try {
      const res = await fetch(`/chat_api/${window.CHAT_USER_ID}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
      });

      const data = await res.json();
      removeTyping();
      appendMessage(data.reply || "No response received.", "bot");

    } catch (err) {
      removeTyping();
      appendMessage("Error connecting to server.", "bot");
    }
  }

  chatSendBtn.addEventListener("click", sendMessage);
  chatInput.addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
  });
}

