import re

with open('frontend/templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the HTML block
old_html = r'<div class="glass-panel p-4 h-100 ai-advice-box">.*?</div>\s*</div>'
new_html = """<div class="glass-panel p-4 h-100 ai-advice-box chat-container">
            <div class="d-flex align-items-center justify-content-between mb-3">
                <div class="d-flex align-items-center gap-3">
                    <div class="kpi-icon" style="background: rgba(59,130,246,0.1); color: var(--accent-blue);">
                        <i class="fa-solid fa-robot"></i>
                    </div>
                    <h5 style="font-weight: 700; color: var(--text-dark); margin: 0;">AI Tư vấn</h5>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-outline-secondary" onclick="refreshAiAdvice(true)" id="btnRefreshAiAdvice" title="Tạo gợi ý mới">
                        <i class="fa-solid fa-rotate-right" id="iconRefreshAiAdvice"></i>
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="openBehaviorModal()" id="btnBehavior" title="Phân tích chuỗi hành vi">
                        <i class="fa-solid fa-brain"></i>
                    </button>
                </div>
            </div>
            
            <div id="aiChatHistory" class="chat-history">
                <div class="chat-msg chat-msg-ai" id="aiAdvice">
                    Đang tải dữ liệu...
                </div>
            </div>
            
            <div class="chat-input-wrapper mt-auto">
                <input type="text" id="chatInput" class="chat-input" placeholder="Hỏi AI (VD: Nên cắt giảm mục nào?)..." onkeypress="if(event.key === 'Enter') sendChatMessage()">
                <button class="btn-chat-send" onclick="sendChatMessage()" title="Gửi tin nhắn">
                    <i class="fa-solid fa-paper-plane"></i>
                </button>
            </div>
        </div>"""

content = re.sub(r'<div class="glass-panel p-4 h-100 ai-advice-box">.*?</div>\s*</div>\s*</div>', 
                 new_html + '\n    </div>', content, flags=re.DOTALL)

# Replace the JS block
old_js = r'async function refreshAiAdvice\(force = false\).*?finally \{\s*if \(btn\) btn\.disabled = false;\s*if \(icon\) icon\.className = \'fa-solid fa-rotate-right me-1\';\s*\}\s*\}'

new_js = """async function refreshAiAdvice(force = false) {
    const btn = document.getElementById('btnRefreshAiAdvice');
    const icon = document.getElementById('iconRefreshAiAdvice');
    const chatHistory = document.getElementById('aiChatHistory');
    
    if (btn) btn.disabled = true;
    if (icon) icon.className = 'fa-solid fa-spinner fa-spin';
    
    if (chatHistory) {
        chatHistory.innerHTML = `
            <div class="chat-msg chat-msg-ai" id="aiAdvice">
                <i class="fa-solid fa-spinner fa-spin me-2 text-primary"></i> Đang phân tích dữ liệu...
            </div>`;
    }
    
    try {
        const url = force ? '/api/advice/?force_refresh=true' : '/api/advice/';
        const advRes = await fetch(url, { method: 'POST' });
        const adviceEl = document.getElementById('aiAdvice');
        if (advRes.ok) {
            const advData = await advRes.json();
            if (adviceEl) adviceEl.innerHTML = formatAdviceText(advData.advice);
        } else {
            const errData = await advRes.json().catch(() => ({}));
            if (adviceEl) {
                adviceEl.style.color = 'var(--text-muted)';
                adviceEl.innerText = errData.detail || 'Hãy thêm dữ liệu giao dịch để AI có thể phân tích.';
            }
        }
    } catch (e) {
        console.error('Advice error:', e);
        const adviceEl = document.getElementById('aiAdvice');
        if (adviceEl) {
            adviceEl.style.color = 'var(--accent-red)';
            adviceEl.innerText = 'Lỗi kết nối khi tải lời khuyên AI.';
        }
    } finally {
        if (btn) btn.disabled = false;
        if (icon) icon.className = 'fa-solid fa-rotate-right';
        if (chatHistory) chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;
    
    const chatHistory = document.getElementById('aiChatHistory');
    
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-msg chat-msg-user';
    userMsg.textContent = message;
    chatHistory.appendChild(userMsg);
    
    input.value = '';
    
    const typingMsg = document.createElement('div');
    typingMsg.className = 'chat-typing-indicator';
    typingMsg.innerHTML = '<div class="chat-typing-dot"></div><div class="chat-typing-dot"></div><div class="chat-typing-dot"></div>';
    chatHistory.appendChild(typingMsg);
    
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    try {
        const res = await fetch('/api/advice/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        typingMsg.remove();
        
        const data = await res.json();
        const aiMsg = document.createElement('div');
        aiMsg.className = 'chat-msg chat-msg-ai';
        if (res.ok) {
            aiMsg.innerHTML = formatAdviceText(data.reply);
        } else {
            aiMsg.textContent = data.detail || 'Xin lỗi, đã xảy ra lỗi.';
            aiMsg.style.color = 'var(--accent-red)';
        }
        chatHistory.appendChild(aiMsg);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    } catch (e) {
        typingMsg.remove();
        const aiMsg = document.createElement('div');
        aiMsg.className = 'chat-msg chat-msg-ai';
        aiMsg.textContent = 'Lỗi kết nối tới AI.';
        aiMsg.style.color = 'var(--accent-red)';
        chatHistory.appendChild(aiMsg);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}"""

content = re.sub(old_js, new_js, content, flags=re.DOTALL)

with open('frontend/templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched dashboard.html successfully")
