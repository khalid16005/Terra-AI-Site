import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import io

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Terra AI", page_icon="🌍", layout="wide")

# Кастомный стиль
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
    command = st.text_input("Что сделать?", placeholder="Например: Опиши, что ты видишь")
    
    if st.button("ЗАПУСТИТЬ ТЕРРУ"):
        if img_file and command:
            image = Image.open(img_file)
            
            with st.spinner("🛰️ Связь с орбитой Terra..."):
                try:
                    # В новой библиотеке google-genai нужно использовать полное имя модели
                    # Или попробовать 'gemini-2.0-flash', если 1.5 недоступна
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
                    if "404" in error_msg:
                        st.error("⚠️ Модель не найдена. Пробую альтернативный канал...")
                        # План Б: Если 1.5-flash выдает 404, пробуем 2.0-flash
                        try:
                            response = client.models.generate_content(
                                model="gemini-2.0-flash", 
                                contents=[image, f"Ты ИИ Terra. Отвечай на русском: {command}"]
                            )
                            st.success(response.text)
                        except Exception as e2:
                            st.error(f"Ошибка системы: {e2}")
                    elif "429" in error_msg:
                        st.error("⚠️ Слишком много запросов. Подожди 60 секунд.")
        else:
            st.warning("Бро, нужно и фото, и текст!")

# --- 4. БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("Статус: Online 🛰️")
    st.write("Terra готова к работе.")
    if st.button("Сброс"):
        st.rerun()

st.divider()
st.caption("Terra AI v1.6 | Stable Build 2026")
