import streamlit as st
import edge_tts, asyncio, uuid, os

st.set_page_config(page_title="English TTS AI", page_icon="🔊")
st.title("🔊 English Text to Speech AI")

VOICES = {
    "Aria (Nữ Mỹ - hay nhất)": "en-US-AriaNeural",
    "Jenny (Nữ Mỹ - vui vẻ)": "en-US-JennyNeural",
    "Guy (Nam Mỹ - trầm ấm)": "en-US-GuyNeural",
    "Davis (Nam Mỹ - tin tức)": "en-US-DavisNeural",
}

text = st.text_area("Enter English text", "Hello, this is my AI voice tool built with Streamlit. It's fast and sounds natural.", height=150)
voice_label = st.selectbox("Choose voice", list(VOICES.keys()))

async def gen(text, voice_id):
    file = f"temp_{uuid.uuid4()}.mp3"
    await edge_tts.Communicate(text, voice_id).save(file)
    return file

if st.button("Generate Audio", type="primary"):
    if not text.strip():
        st.warning("Please enter text!")
    else:
        with st.spinner("Generating..."):
            voice_id = VOICES[voice_label]
            audio_file = asyncio.run(gen(text, voice_id))
            st.audio(audio_file)
            with open(audio_file, "rb") as f:
                st.download_button("Download MP3", f, file_name="tts.mp3", mime="audio/mp3")
            os.remove(audio_file) # xóa file tạm