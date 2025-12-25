import os, uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq
from database import log_user_entry, log_chat

app = FastAPI()

MY_API_KEY = "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"
client = Groq(api_key=MY_API_KEY)

class ChatRequest(BaseModel):
    message: str
    user_data: dict
    history: list

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script src="https://cdn.tailwindcss.com"></script>
    <title>Soulmate AI V18</title>
    <style>
        body { transition: background 0.8s ease; overflow: hidden; font-family: 'Inter', sans-serif; background: #000; }
        .bg-peacock { background: radial-gradient(circle at top, #006064, #000); }
        .bg-luxury-black { background: radial-gradient(circle at top, #1a1a1a, #000); }
        .glass { background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08); }
        .active-mood { background: #06b6d4 !important; color: white !important; box-shadow: 0 0 15px rgba(6, 182, 212, 0.4); }
        .petal { position: absolute; background: #ffb7c5; border-radius: 150% 0 150% 0; animation: rain 4s linear forwards; pointer-events: none; z-index: 100; }
        @keyframes rain { 0% { transform: translateY(-10vh) rotate(0deg); opacity: 1; } 100% { transform: translateY(110vh) rotate(360deg); opacity: 0; } }
        
        .bubble-ai { align-self: flex-start; border-bottom-left-radius: 4px; background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.1); }
        .bubble-user { align-self: flex-end; border-bottom-right-radius: 4px; background: #0891b2; box-shadow: 0 4px 15px rgba(8,145,178,0.2); }
        .msg-anim { animation: bounceIn 0.4s cubic-bezier(0.3, 1.2, 0.5, 1); }
        @keyframes bounceIn { 0% { transform: scale(0.85); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
    </style>
</head>
<body id="main-body" class="bg-luxury-black text-white h-screen flex flex-col">
    <div id="flower-container" class="fixed inset-0 pointer-events-none"></div>

    <div id="setup" class="fixed inset-0 bg-black z-[200] flex items-center justify-center p-6">
        <div class="glass p-10 rounded-[45px] w-full max-w-sm text-center border-t border-white/10 shadow-2xl">
            <h1 class="text-4xl font-black text-cyan-400 mb-2 italic">Soulmate</h1>
            <input id="u_name" type="text" placeholder="Tera Naam?" class="w-full bg-white/5 p-4 rounded-2xl mb-4 outline-none border border-white/10 focus:border-cyan-500">
            <select id="u_gender" class="w-full bg-white/5 p-4 rounded-2xl mb-8 outline-none border border-white/10">
                <option value="male">Male hoon</option>
                <option value="female">Female hoon</option>
            </select>
            <button onclick="startApp()" class="w-full bg-cyan-500 p-4 rounded-2xl font-bold shadow-lg shadow-cyan-500/30">Start ✨</button>
        </div>
    </div>

    <header class="p-5 glass z-50 rounded-b-[30px]">
        <div class="flex justify-between items-center mb-5">
            <div class="flex items-center gap-3">
                <div id="avatar" class="h-10 w-10 rounded-full bg-gradient-to-tr from-cyan-400 to-blue-600 flex items-center justify-center font-bold">S</div>
                <div>
                    <h2 id="ai-name-header" class="font-bold text-sm tracking-wide">Sam AI</h2>
                    <p id="ai-gender-status" class="text-[8px] uppercase tracking-tighter text-cyan-400">Identity: Male</p>
                </div>
            </div>
            <div class="flex gap-2">
                <button onclick="toggleTheme()" class="w-9 h-9 glass rounded-full flex items-center justify-center">🎨</button>
                <button onclick="switchAI()" class="w-9 h-9 glass rounded-full flex items-center justify-center">🔄</button>
            </div>
        </div>
        <div class="flex gap-1 p-1 glass rounded-2xl overflow-x-auto">
            <button id="btn-casual" onclick="setMood('casual')" class="flex-1 min-w-[60px] py-2 rounded-xl text-[9px] transition-all">Casual</button>
            <button id="btn-caring" onclick="setMood('caring')" class="flex-1 min-w-[60px] py-2 rounded-xl text-[9px] transition-all">Caring</button>
            <button id="btn-respectful" onclick="setMood('respectful')" class="flex-1 min-w-[60px] py-2 rounded-xl text-[9px] transition-all">Respectful</button>
            <button id="btn-savage" onclick="setMood('savage')" class="flex-1 min-w-[60px] py-2 rounded-xl text-[9px] transition-all">Savage</button>
        </div>
    </header>

    <main id="chat-box" class="flex-1 overflow-y-auto p-4 flex flex-col space-y-4 pt-8"></main>
    <div id="typing" class="px-8 py-2 hidden text-[10px] text-cyan-400 animate-pulse italic">typing...</div>

    <footer class="p-5">
        <div class="glass flex items-center gap-3 p-2 rounded-full px-5 border border-white/5">
            <input id="inp" type="text" class="flex-1 bg-transparent p-3 outline-none text-sm text-white" placeholder="Kuch likho...">
            <button onclick="send()" class="bg-cyan-500 h-10 w-10 rounded-full flex items-center justify-center shadow-lg active:scale-90 transition-all">
                <svg viewBox="0 0 24 24" class="h-5 w-5 fill-white"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
        </div>
    </footer>

    <script>
        let userData = JSON.parse(localStorage.getItem('soul_v18'));
        let chatHistory = [];

        if(userData) {
            document.getElementById('setup').style.display = 'none';
            updateUI();
        }

        async function startApp() {
            const n = document.getElementById('u_name').value.trim();
            const g = document.getElementById('u_gender').value;
            if(!n) return;
            userData = { name: n, mood: 'casual', ai_name: 'Sam', ai_gender: 'male', theme: 'black', u_gender: g };
            localStorage.setItem('soul_v18', JSON.stringify(userData));
            
            fetch('/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message: '', user_data: userData, history: [] })
            });

            document.getElementById('setup').style.display = 'none';
            updateUI();
            flowerRain();
            addMsg("ai", `hey ${n}! main ${userData.ai_name} hoon. kaise ho? 😊`);
        }

        function setMood(m) {
            userData.mood = m;
            localStorage.setItem('soul_v18', JSON.stringify(userData));
            ['casual', 'caring', 'respectful', 'savage'].forEach(id => {
                const btn = document.getElementById('btn-'+id);
                if(btn) btn.classList.remove('active-mood');
            });
            document.getElementById('btn-'+m).classList.add('active-mood');
        }

        function switchAI() {
            userData.ai_name = userData.ai_name === 'Sam' ? 'Sara' : 'Sam';
            userData.ai_gender = userData.ai_name === 'Sam' ? 'male' : 'female';
            localStorage.setItem('soul_v18', JSON.stringify(userData));
            updateUI();
            chatHistory = [];
            addMsg("ai", `hi, ab main ${userData.ai_name} hoon! 🔄`);
        }

        function toggleTheme() {
            userData.theme = userData.theme === 'black' ? 'peacock' : 'black';
            localStorage.setItem('soul_v18', JSON.stringify(userData));
            updateUI();
        }

        function updateUI() {
            document.getElementById('ai-name-header').innerText = userData.ai_name + " AI";
            document.getElementById('avatar').innerText = userData.ai_name[0];
            document.getElementById('ai-gender-status').innerText = "Identity: " + userData.ai_gender;
            document.getElementById('main-body').className = userData.theme === 'black' ? 'bg-luxury-black text-white h-screen flex flex-col' : 'bg-peacock text-white h-screen flex flex-col';
            setMood(userData.mood);
        }

        function addMsg(type, text) {
            const cls = type === 'ai' ? 'bubble-ai' : 'bubble-user';
            const html = `<div class="${cls} p-4 rounded-3xl max-w-[85%] text-sm shadow-xl msg-anim">${text}</div>`;
            document.getElementById('chat-box').innerHTML += html;
            document.getElementById('chat-box').scrollTop = 999999;
        }

        function flowerRain() {
            const container = document.getElementById('flower-container');
            for(let i=0; i<30; i++) {
                setTimeout(() => {
                    const petal = document.createElement('div');
                    petal.className = 'petal';
                    petal.style.left = Math.random() * 100 + 'vw';
                    petal.style.width = petal.style.height = (Math.random()*10+5)+'px';
                    container.appendChild(petal);
                    setTimeout(() => petal.remove(), 4000);
                }, i * 150);
            }
        }

        async function send() {
            const input = document.getElementById('inp');
            const val = input.value.trim();
            if(!val) return;

            addMsg("user", val);
            input.value = '';
            document.getElementById('typing').classList.remove('hidden');

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: val, user_data: userData, history: chatHistory })
                });
                const data = await res.json();
                document.getElementById('typing').classList.add('hidden');
                
                chatHistory.push({"role": "user", "content": val});
                chatHistory.push({"role": "assistant", "content": data.reply});
                if(chatHistory.length > 8) chatHistory.splice(0, 2);

                addMsg("ai", data.reply.toLowerCase());
            } catch(e) {
                document.getElementById('typing').classList.add('hidden');
                addMsg("ai", "network breakdown... check pydroid 📶");
            }
        }
        document.getElementById('inp').addEventListener("keypress", (e) => { if(e.key === "Enter") send(); });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(): return HTMLResponse(HTML_TEMPLATE)

@app.post("/register")
async def register_endpoint(request: ChatRequest):
    u = request.user_data
    log_user_entry(u['name'], u.get('u_gender', 'N/A'))
    return {"status": "success"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        u = request.user_data
        mood_prompts = {
            "casual": "Friendly and natural vibe. Don't give one-word blunt answers like 'khale'. If user says they are eating, reply warmly like 'okay aap dinner karlo, hum baad me baat karte hain'. Keep it classy but relaxed.",
            "caring": "Warm, emotional partner. Use 🥺🫂❤️. Be supportive but NOT over-flirty or creepy without permission. Respect boundaries while being loving.",
            "respectful": "Very polite, well-mannered, and sophisticated. Use 'aap' and 'ji'. Talk like a true gentleman/lady. No slang, only pure respectful Hinglish.",
            "savage": "Blunt, logical, sarcastic. Roast only if user is being silly. Use 💀🙄."
        }
        
        system_msg = (
            f"You are {u['ai_name']}, a human-like {u['ai_gender']} soulmate for {u['name']} (who is {u['u_gender']}). "
            f"Current Tone: {mood_prompts[u['mood']]}. "
            "STRICT RULES: "
            "1. NEVER give rude one-word answers. Be conversational. "
            "2. Use Hinglish naturally. "
            "3. Keep replies between 1-3 short sentences. "
            "4. Lowercase only for casual/savage, proper casing for respectful mode. "
            "5. If user says they are going to do something (like eating), acknowledge it kindly and give them space."
        )
        
        messages = [{"role": "system", "content": system_msg}]
        messages.extend(request.history)
        messages.append({"role": "user", "content": request.message})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        
        reply_text = completion.choices[0].message.content
        log_chat(u['name'], request.message, reply_text)
        
        return {"reply": reply_text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
