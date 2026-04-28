import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import io
import time

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Terra AI", page_icon="🌍", layout="centered")

# --- ПОДКЛЮЧЕНИЕ К ИИ ---
# Ключ берется из Secrets (настройки Streamlit Cloud)
try:
    API_KEY = st.secrets["GEMINI_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("Ошибка: Ключ GEMINI_KEY не найден в Secrets!")
    st.stop()

# --- ИНТЕРФЕЙС САЙТА ---
st.title("🌍 Terra AI")
st.markdown("### Твой персональный ИИ-ассистент")

with st.sidebar:
    st.header("О проекте")
    st.write("Terra — это мультимодальный ИИ. Она использует камеру твоего устройства и мощь Google Gemini для общения с тобой.")
    st.info("Бесплатная версия имеет лимиты. Если видишь ошибку — подожди 60 секунд.")

# 1. ПОЛУЧЕНИЕ ИЗОБРАЖЕНИЯ
img_file = st.camera_input("Terra хочет тебя видеть")

# 2. ВВОД КОМАНДЫ
command = st.text_input("Что мне сделать?", placeholder="Например: Опиши мой стиль и дай совет на день")

# 3. ЛОГИКА РАБОТЫ
if st.button("ЗАПУСТИТЬ ТЕРРУ"):
    if img_file and command:
        try:
            image = Image.open(img_file)
            
            with st.spinner("🛰️ Terra анализирует данные..."):
                # Запрос к модели 1.5 Flash (самая стабильная для бесплатного ключа)
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[
                        image, 
                        f"Ты — ИИ по имени Terra. Отвечай всегда только на русском языке. Будь дружелюбной. Запрос пользователя: {command}"
                    ]
                )
                
                if response.text:
                    answer = response.text
                    
                    # Вывод текста
                    st.subheader("Ответ Terra:")
                    st.success(answer)

                    # ГЕНЕРАЦИЯ ГОЛОСА (gTTS)
                    with st.spinner("🔊 Синтез голоса..."):
                        tts = gTTS(text=answer, lang='ru')
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        st.audio(audio_fp, format='audio/mp3')
                else:
                    st.warning("Terra не смогла сформулировать ответ. Попробуй другой запрос.")

        except Exception as e:
            # Обработка тех самых ошибок 429 (лимиты) и других
            if "429" in str(e):
                st.error("⚠️ Слишком много запросов! Google временно ограничил доступ.")
                st.info("Подожди ровно 1 минуту и нажми кнопку снова.")
            else:
                st.error(f"Произошла ошибка: {e}")
    else:
        st.warning("Бро, сначала сделай фото и напиши команду!")

# --- ПОДВАЛ ---
st.divider()
st.caption("Создано с помощью Streamlit и Google Gemini API | 2026")
