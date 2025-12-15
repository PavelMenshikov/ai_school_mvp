import streamlit as st
import requests
import streamlit.components.v1 as components
import subprocess
import sys
import time
import os

def run_backend():
    
    try:
        requests.get("http://127.0.0.1:8000/tutors", timeout=1)
        return 
    except:
        pass 

    print("🚀 Запускаем Backend-сервер в фоне...")
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    time.sleep(3) 

run_backend()


API_URL = "http://127.0.0.1:8000"
DEMO_TIME_SECONDS = 180 

st.set_page_config(layout="wide", page_title="AI School Demo", page_icon="🎓")


st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold;}
    .reportview-container .main .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 AI School Platform")


tutors = []
try:
    for _ in range(5):
        try:
            resp = requests.get(f"{API_URL}/tutors", timeout=2)
            if resp.status_code == 200:
                tutors = resp.json()
                break
        except:
            time.sleep(1)
except:
    st.error("❌ Ошибка: Сервер не отвечает. Попробуйте обновить страницу.")
    st.stop()

if not tutors:
    st.warning("🔄 Загрузка системы... Обновите страницу через 5 секунд.")
    st.stop()


with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.markdown("### Профиль студента")
    st.info("👤 Demo User")
    st.write("💳 Баланс: **500 мин.**")
    st.divider()
    
    st.markdown("### Выбор наставника")
    tutor_names = [t['name'] for t in tutors]
    selected = st.selectbox("Репетитор:", tutor_names)
    
    st.warning("⚠️ Лимит: 10 одновременных сессий")


if 'active' not in st.session_state:
    st.session_state.active = False
if 'url' not in st.session_state:
    st.session_state.url = ""


if not st.session_state.active:
    st.markdown(f"## 👋 Готовы начать урок с {selected}?")
    st.write("Нажмите кнопку ниже. Система проверит очередь и создаст защищенное соединение.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("▶️ НАЧАТЬ УРОК", type="primary"):
            with st.spinner("Генерация токена доступа..."):
                try:
                    resp = requests.post(f"{API_URL}/session/start").json()
                    if resp['status'] == "active":
                        st.session_state.active = True
                        st.session_state.url = resp['url']
                        st.rerun()
                    else:
                        st.warning(f"⏳ Вы в очереди. Позиция: {resp['pos']}")
                except Exception as e:
                    st.error(f"Ошибка сервера: {e}")


else:
    c1, c2 = st.columns([3, 1])
    
    with c1:
        
        timer_html = f"""
        <div style="background: #f0f2f6; padding: 10px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #ccc;">
            <span style="font-weight: bold; color: #333;">🔴 LIVE RECORDING</span>
            <span id="timer" style="font-family: monospace; font-size: 20px; font-weight: bold; color: #d93025;">Loading...</span>
        </div>
        <script>
        var timeLeft = {DEMO_TIME_SECONDS};
        var timerId = setInterval(function(){{
            if(timeLeft <= 0){{
                document.getElementById("timer").innerHTML = "ВРЕМЯ ВЫШЛО";
                clearInterval(timerId);
            }} else {{
                var m = Math.floor(timeLeft / 60);
                var s = timeLeft % 60;
                document.getElementById("timer").innerHTML = m + ":" + (s < 10 ? "0" : "") + s;
                timeLeft--;
            }}
        }}, 1000);
        </script>
        """
        components.html(timer_html, height=60)

       
        iframe_html = f"""
        <iframe 
            src="{st.session_state.url}" 
            width="100%" 
            height="550px" 
            frameborder="0" 
            allow="camera *; microphone *; autoplay *; encrypted-media *; fullscreen *; display-capture *;"
            style="border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);"
        ></iframe>
        """
        components.html(iframe_html, height=560)
        
        
        if st.button("⏹ ЗАВЕРШИТЬ УРОК"):
            requests.post(f"{API_URL}/session/end")
            st.session_state.active = False
            st.rerun()

    with c2:
        st.markdown("### 📝 Заметки")
        st.text_area("Конспект урока", height=300)
        st.info("💡 Если вас не слышно: Нажмите на шестеренку в видео и выберите 'Communications' или другой микрофон.")
    st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px; margin-top: 20px; font-family: monospace;'>
        Made with ☕ and 🚬
    </div>
    """,
    unsafe_allow_html=True
)    