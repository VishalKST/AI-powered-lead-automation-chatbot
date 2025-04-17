function sendMessage(message = null) {
  const inputBox = document.getElementById("userInput");
  const userMessage = message || inputBox.value;
  if (!userMessage.trim()) return;

  // Simple client-side numeric check for budget (optional)
  if (lastBotMessage.includes("budget") && isNaN(userMessage.replace(/,/g, ''))) {
    alert("❌ Please enter your budget as a number only (e.g., 10000).");
    return;
  }

  document.getElementById("chatbox").innerHTML += `<div><b>You:</b> ${userMessage}</div>`;
  inputBox.value = "";
  document.getElementById("buttonOptions").innerHTML = "";

  fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage, session_id, lang })
  })
  .then(res => res.json())
  .then(data => {
    lastBotMessage = data.response; // Store last response for context
    document.getElementById("chatbox").innerHTML += `<div><b>Bot:</b> ${data.response}</div>`;
    document.getElementById("chatbox").scrollTop = document.getElementById("chatbox").scrollHeight;

    if (data.options && data.options.length > 0) {
      const buttonGroup = document.getElementById("buttonOptions");
      data.options.forEach(option => {
        const btn = document.createElement("button");
        btn.textContent = option;
        btn.className = "option-button";
        btn.onclick = () => sendMessage(option);
        buttonGroup.appendChild(btn);
      });
    }
  })
  .catch(err => {
    document.getElementById("chatbox").innerHTML += `<div><b>Bot:</b> Error: ${err}</div>`;
  });
}

let lastBotMessage = ""; // Add this line at the top of your script
