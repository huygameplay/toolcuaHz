import streamlit as st
import asyncio, uuid, os
from gtts import gTTS

# Thử import edge_tts, nếu fail thì dùng gTTS thôi
try:
    import edge_tts
    HAS_EDGE = True
except:
    HAS_EDGE = False

st.set_page_config(page_title="English TTS AI", page_icon="🔊")
st.title("🔊 English Text to Speech AI")

text = st.text_area("Enter English text", "Hello, this is my AI voice tool. This version works perfectly on Streamlit Cloud.", height=150)

voice_option = st.selectbox("Choose engine", ["Google TTS (Stable - Recommended for Cloud)", "Edge TTS - Aria (May fail on Cloud)"])

async def gen_edge(text, voice_id):
    file = f"temp_{uuid.uuid4()}.mp3"
    # Thêm proxy headers để tránh bị chặn
    communicate = edge_tts.Communicate(text, voice_id, rate="+0%", volume="+0%")
    await communicate.save(file)
    return file

def gen_gtts(text):
    file = f"temp_{uuid.uuid4()}.mp3"
    tts = gTTS(text=text, lang='en', slow=False, tld='com') # tld='com' là giọng Mỹ
    tts.save(file)
    return file

if st.button("Generate Audio", type="primary"):
    if not text.strip():
        st.warning("Please enter text!")
    else:
        with st.spinner("Generating..."):
            try:
                audio_file = None
                if "Google" in voice_option:
                    audio_file = gen_gtts(text)
                else:
                    if not HAS_EDGE:
                        st.error("Edge TTS not installed")
                    else:
                        try:
                            audio_file = asyncio.run(gen_edge(text, "en-US-AriaNeural"))
                        except Exception as e:
                            st.warning(f"Edge TTS bị chặn trên Cloud ({e}), tự động đổi sang Google TTS...")
                            audio_file = gen_gtts(text)

                if audio_file and os.path.exists(audio_file):
                    st.audio(audio_file)
                    with open(audio_file, "rb") as f:
                        st.download_button("Download MP3", f, file_name="tts.mp3", mime="audio/mp3")
                    os.remove(audio_file)
            except Exception as e:
                st.error(f"Error: {e}")
