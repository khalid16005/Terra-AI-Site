import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import io

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Terra AI", page_icon="🌍", layout="wide")

# Кастомный стиль для красоты
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #0078ff; color: white; }
    .stTextInput>div>div>input { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ПОДКЛЮЧЕНИЕ КЛЮЧА ---
try:
    API_KEY = st.secrets["GEMINI_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("🚨 Ошибка: Проверь 'GEMINI_KEY' в настройках Secrets на Streamlit!")
    st.stop()

# --- 3. ИНТЕРФЕЙС ---
st.title("🌍 Terra AI System")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("👁️ Зрение Терры")
    img_file = st.camera_input("Сделай снимок")

with col2:
    st.subheader("💬 Команды")
    command = st.text_input("Что сделать?", placeholder="Например: Расскажи анекдот по этому фото")
    
    if st.button("ЗАПУСТИТЬ ТЕРРУ"):
        if img_file and command:
            image = Image.open(img_file)
            
            with st.spinner("🛰️ Связь с орбитой Terra..."):
                try:
                    # Пытаемся использовать 1.5 Flash (она стабильнее для фри-ключа)
                    response = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        contents=[
                            image, 
                            f"Ты — ИИ по имени Terra. Отвечай кратко, дружелюбно и только на русском. Запрос: {command}"
                        ]
                    )
                    
                    if response.text:
                        answer = response.text
                        st.success("✅ Ответ получен!")
                        st.write(f"**Terra:** {answer}")

                        # Голос
                        tts = gTTS(text=answer, lang='ru')
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        st.audio(audio_fp, format='audio/mp3')
                
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg:
                        st.error("⚠️ Лимит запросов исчерпан. Подожди 60 секунд.")
                        st.info("Это ограничение бесплатного ключа Google. Просто дай системе отдохнуть.")
                    else:
                        st.error(f"Произошла ошибка: {error_msg}")
        else:
            st.warning("Бро, нужно и фото, и текст!")

# --- 4. БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("Статус: Online 🛰️")
    st.markdown("---")
    st.write("**Совет:** Если Terra молчит, подожди минуту. Бесплатные ключи имеют лимиты на скорость запросов.")
    if st.button("Очистить всё"):
        st.rerun()

st.divider()
st.caption("Terra AI v1.5 | 2026 Stable Build")
