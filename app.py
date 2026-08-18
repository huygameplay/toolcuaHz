import os
import streamlit as st
import yt_dlp

st.set_page_config(page_title="TikTok MP3 Downloader", page_icon="🎵", layout="centered")

st.title("🎵 Tải Âm Thanh TikTok sang MP3")
st.write("Dán link video TikTok bất kỳ để trích xuất và tải file âm thanh về máy.")

# Ô nhập link
tiktok_url = st.text_input("Nhập Link Video TikTok:")

if st.button("Tải Âm Thanh", type="primary"):
    if not tiktok_url:
        st.warning("Vui lòng nhập link TikTok!")
    else:
        with st.spinner("Đang xử lý và tải âm thanh..."):
            output_dir = "downloads"
            os.makedirs(output_dir, exist_ok=True)
            
            # Cấu hình yt-dlp để tải và chuyển đổi sang mp3
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(tiktok_url, download=True)
                    video_id = info.get("id", "audio")
                    title = info.get("title", "TikTok Audio")
                    mp3_path = os.path.join(output_dir, f"{video_id}.mp3")

                st.success(f"Đã tải thành công: **{title}**")
                
                # Nút tải file về máy
                with open(mp3_path, "rb") as f:
                    st.download_button(
                        label="📥 Click để tải file MP3 về máy",
                        data=f,
                        file_name=f"{title[:50]}.mp3",
                        mime="audio/mpeg"
                    )
                
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
