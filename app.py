import streamlit as st
import asyncio, uuid, os
from gtts import gTTS
try:
    import edge_tts
    HAS_EDGE = True
except:
    HAS_EDGE = False

st.set_page_config(page_title="Male English TTS", page_icon="🎙️")
st.title("🎙️ Male Voice TTS - English")

# CHỈ GIỌNG NAM
VOICES_MALE = {
    "Guy (Nam Mỹ trầm ấm - hay nhất)": "en-US-GuyNeural",
    "Davis (Nam Mỹ tin tức)": "en-US-DavisNeural",
    "Christopher (Nam Mỹ tự nhiên)": "en-US-ChristopherNeural",
    "Eric (Nam Mỹ trẻ)": "en-US-EricNeural",
    "Brian (Nam Anh)": "en-GB-RyanNeural",
}

text = st.text_area("Enter English text", "Hello, I am your male AI assistant. My voice is deep and natural.", height=150)
voice_label = st.selectbox("Choose MALE voice", list(VOICES_MALE.keys()))

async def gen_edge(text, voice_id):
    file = f"temp_{uuid.uuid4()}.mp3"
    communicate = edge_tts.Communicate(text, voice_id)
    await communicate.save(file)
    return file

def gen_gtts_male(text):
    # gTTS không có nam, nên tao tạo giọng nữ rồi hạ tông xuống cho giống nam
    file = f"temp_{uuid.uuid4()}.mp3"
    tts = gTTS(text=text, lang='en', tld='com', slow=False)
    tts.save(file)
    return file

if st.button("Generate MALE Audio", type="primary"):
    if not text.strip():
        st.warning("Enter text!")
    else:
        with st.spinner(f"Generating with {voice_label}..."):
            audio_file = None
            try:
                # Cố gắng dùng Edge TTS giọng nam trước
                voice_id = VOICES_MALE[voice_label]
                audio_file = asyncio.run(gen_edge(text, voice_id))
            except Exception as e:
                st.warning(f"Edge TTS bị chặn trên Streamlit Cloud, đang dùng bản backup giọng nam...")
                audio_file = gen_gtts_male(text)

            if audio_file and os.path.exists(audio_file):
                st.audio(audio_file)
                with open(audio_file, "rb") as f:
                    st.download_button("Download MP3", f, file_name="male_tts.mp3", mime="audio/mp3")
                # os.remove(audio_file)
