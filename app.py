import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import io

# Подключаем ключ (мы добавим его в настройки позже)
API_KEY = st.secrets["GEMINI_KEY"]
client = genai.Client(api_key=API_KEY)

st.set_page_config(page_title="Terra AI", page_icon="🌍")

# Описание, которое мы выбрали
st.title("🌍 Terra AI")
st.markdown("### Твой персональный ИИ с компьютерным зрением")

with st.expander("Что такое Terra? Узнать больше"):
    st.write("Terra — это ИИ нового поколения. Она видит тебя, слышит твои команды и говорит на русском языке.")

# 1. Камера
img_file = st.camera_input("Terra смотрит на тебя...")

# 2. Поле для команды
command = st.text_input("Что мне сделать?", placeholder="Например: Опиши мой стиль и нарисуй меня в будущем")

if st.button("ЗАПУСК"):
    if img_file and command:
        image = Image.open(img_file)
        
        # Terra думает
        with st.spinner("Terra анализирует..."):
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[f"Ты — ИИ по имени Terra. Отвечай только на русском. Запрос пользователя: {command}", image]
            )
            
            answer = response.text
            st.success(answer)

            # Голос (теперь работает прямо в браузере!)
            tts = gTTS(text=answer, lang='ru')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format='audio/mp3')
    else:
        st.warning("Сделай фото и введи команду, бро!")
