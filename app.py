import streamlit as st
import requests
import streamlit.components.v1 as components
import subprocess
import sys
import time

def run_backend():
    try:
        requests.get("http://127.0.0.1:8000/tutors", timeout=1)
        return
    except:
        print("🚀 Starting Backend...")        
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)

run_backend()


API_URL = "http://127.0.0.1:8000"
DEMO_SECONDS = 180 

st.set_page_config(layout="wide", page_title="AI School Demo", page_icon="🎓")


st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold;}
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 AI School Platform")

tutors = []
try:
    for _ in range(5):
        try:
            resp = requests.get(f"{API_URL}/tutors", timeout=1)
            if resp.status_code == 200:
                tutors = resp.json()
                break
        except:
            time.sleep(1)
except:
    st.error("Connecting to server...")
    st.stop()

if not tutors:
    st.warning("Loading...")
    time.sleep(1)
    st.rerun()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.info("👤 Demo User")
    st.write("💳 Баланс: **500 мин.**")
    st.divider()
    tutor_names = [t['name'] for t in tutors]
    selected = st.selectbox("Репетитор:", tutor_names)
    st.warning("⚠️ Лимит: 10 сессий")

# Logic
if 'active' not in st.session_state:
    st.session_state.active = False
if 'url' not in st.session_state:
    st.session_state.url = ""

if not st.session_state.active:
    st.markdown(f"## 👋 Урок с {selected}")
    st.write("Нажмите кнопку ниже для начала.")
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("▶️ НАЧАТЬ УРОК", type="primary"):
            with st.spinner("Создание комнаты..."):
                try:
                    resp = requests.post(f"{API_URL}/session/start").json()
                    if resp['status'] == "active":
                        st.session_state.active = True
                        st.session_state.url = resp['url']
                        st.rerun()
                    else:
                        st.warning(f"⏳ Очередь: {resp['pos']}")
                except:
                    st.error("Ошибка API")
else:
    c1, c2 = st.columns([3, 1])
    with c1:
        
        components.html(f"""
        <div style="background:#f0f2f6;padding:10px;border-radius:8px;display:flex;justify-content:space-between;border:1px solid #ccc;">
            <span style="font-weight:bold;">🔴 LIVE</span>
            <span id="t" style="font-family:monospace;font-weight:bold;color:#d93025;">Loading...</span>
        </div>
        <script>
        var t={DEMO_SECONDS};setInterval(function(){{
            if(t<=0)document.getElementById("t").innerHTML="END";
            else{{var m=Math.floor(t/60),s=t%60;document.getElementById("t").innerHTML=m+":"+(s<10?"0":"")+s;t--;}}
        }},1000);
        </script>
        """, height=60)

        
        components.html(f"""
        <iframe src="{st.session_state.url}" width="100%" height="550px" frameborder="0" 
        allow="camera *; microphone *; autoplay *; encrypted-media *; fullscreen *; display-capture *;"
        style="border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.15);"></iframe>
        """, height=560)
        
        if st.button("⏹ ЗАВЕРШИТЬ"):
            requests.post(f"{API_URL}/session/end")
            st.session_state.active = False
            st.rerun()

    with c2:
        st.write("### Заметки")
        st.text_area("...", height=300)


st.divider()
st.markdown("<div style='text-align:center;color:#666;font-size:12px;font-family:monospace;'>Made with ☕ and 🚬</div>", unsafe_allow_html=True)