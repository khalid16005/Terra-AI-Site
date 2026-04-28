import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import io

# --- 1. НАСТРОЙКИ ИНТЕРФЕЙСА ---
st.set_page_config(page_title="Terra AI", page_icon="🌍")
st.title("🌍 Terra AI System")
st.markdown("---")

# --- 2. ПОДКЛЮЧЕНИЕ КЛЮЧА ---
try:
    # Берем ключ из Secrets (Streamlit Cloud)
    API_KEY = st.secrets["GEMINI_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("Критическая ошибка: Проверь настройки Secrets в Streamlit!")
    st.stop()

# --- 3. ИНТЕРФЕЙС САЙТА ---
with st.sidebar:
    st.header("Статус системы")
    st.success("Terra Online 🛰️")
    st.info("Если лимит превышен (ошибка 429), подожди 60 секунд.")

# Камера
img_file = st.camera_input("Сделай фото для анализа")

# Текстовое поле
command = st.text_input("Твой запрос к Terra:", placeholder="Например: Кто на фото и как мне поднять настроение?")

# --- 4. ЛОГИКА РАБОТЫ ---
if st.button("ЗАПУСК TERRA"):
    if img_file and command:
        try:
            image = Image.open(img_file)
            
            with st.spinner("🧠 Terra обрабатывает данные..."):
                # Используем gemini-2.0-flash (актуальная модель)
                # Если всё равно будет 404, попробуй заменить на "gemini-1.5-flash"
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[
                        image, 
                        f"Ты — ИИ по имени Terra. Отвечай кратко и только на русском. Запрос: {command}"
                    ]
                )
                
                if response.text:
                    answer = response.text
                    
                    # Вывод ответа
                    st.subheader("Ответ:")
                    st.write(answer)

                    # Озвучка
                    with st.spinner("🔊 Генерирую голос..."):
                        tts = gTTS(text=answer, lang='ru')
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        st.audio(audio_fp, format='audio/mp3')
                else:
                    st.warning("Terra не смогла прочитать данные. Попробуй еще раз.")

        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                st.error("⚠️ Слишком много запросов. Подожди минуту.")
            elif "404" in error_str:
                st.error("⚠️ Ошибка 404: Модель не найдена. Попробуй в коде сменить 'gemini-2.0-flash' на 'gemini-1.5-flash'.")
            else:
                st.error(f"Ошибка: {error_str}")
    else:
        st.warning("Нужно и фото, и команда, бро!")

st.markdown("---")
st.caption("Terra AI v1.0 | Powered by Google Gemini")
