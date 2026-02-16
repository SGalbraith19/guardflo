const chatWindow = document.getElementById("chat-window");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

sendBtn.onclick = sendMessage;
input.addEventListener("keypress", function(e){
   if(e.key === "Enter") sendMessage();
});

function sendMessage(){
   const text = input.value.trim();
   if(!text) return;

   appendMessage(text, "user-message");
   input.value = "";

   setTimeout(() => {
       appendMessage("Authoritative response placeholder.", "ai-message");
   }, 600);
}

function appendMessage(text, className){
   const msg = document.createElement("div");
   msg.className = "message " + className;
   msg.textContent = text;
   chatWindow.appendChild(msg);
   chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showTab(id){
   document.querySelectorAll(".tab").forEach(t => t.style.display="none");
   document.getElementById(id).style.display="block";

   document.querySelectorAll(".sidebar button")
       .forEach(b => b.classList.remove("active"));

   event.target.classList.add("active");
}

document.getElementById("dark-toggle").onchange = function(){
   document.body.classList.toggle("dark", this.checked);
};