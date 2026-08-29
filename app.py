import streamlit as st
import yt_dlp
import os
import tempfile
import re
import requests
import shutil

st.set_page_config(page_title="TikTok Downloader Pro V2", page_icon="🎵", layout="centered")

st.title("🎵 TikTok Downloader V2 - Fix Lỗi")
st.caption("Bản fix chạy mượt trên Streamlit Cloud")

def is_valid_tiktok_url(url):
    return "tiktok.com" in url or "vt.tiktok.com" in url

# --- HÀM FALLBACK DÙNG API (Khi yt-dlp bị chặn) ---
def download_via_tikwm_api(url):
    try:
        api_url = "https://www.tikwm.com/api/"
        payload = {"url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1}
        resp = requests.post(api_url, data=payload, timeout=15).json()
        if resp.get("code") == 0:
            data = resp.get("data")
            return {
                "title": data.get("title", "TikTok Video"),
                "thumbnail": data.get("cover"),
                "author": data.get("author", {}).get("unique_id", ""),
                "video_url": data.get("play"), # no watermark
                "music_url": data.get("music"),
                "like_count": data.get("digg_count", 0),
                "duration": data.get("duration", 0)
            }
    except Exception as e:
        print(f"API Error: {e}")
    return None

def download_file_from_url(file_url):
    temp_dir = tempfile.mkdtemp()
    r = requests.get(file_url, stream=True, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
    ext = ".mp4" if "video" in r.headers.get("Content-Type","") or "mp4" in file_url else ".mp3"
    if "music" in file_url or file_url.endswith(".mp3"):
        ext = ".mp3"
    filepath = os.path.join(temp_dir, f"tiktok{ext}")
    with open(filepath, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    return filepath

# --- HÀM CHÍNH YT-DLP ---
def download_with_ytdlp(url, mode, progress_bar):
    temp_dir = tempfile.mkdtemp()
    
    # Kiểm tra có ffmpeg không
    has_ffmpeg = shutil.which("ffmpeg") is not None
    
    ydl_opts_base = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'http_headers': {'User-Agent': 'Mozilla/5.0'},
    }

    if "Video" in mode:
        ydl_opts_base['format'] = 'bestvideo+bestaudio/best'
        ydl_opts_base['merge_output_format'] = 'mp4'
    else:
        # Nếu không có ffmpeg, tải file gốc mp4 rồi đổi tên, client tự nghe được
        # Nếu có ffmpeg thì convert sang mp3
        ydl_opts_base['format'] = 'bestaudio/best'
        if has_ffmpeg:
            ydl_opts_base['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

    def hook(d):
        if d['status'] == 'downloading':
            try:
                percent_str = d.get('_percent_str','0%').replace('%','').strip()
                p = float(percent_str) / 100
                progress_bar.progress(min(p, 1.0), text=f"Đang tải... {percent_str}%")
            except: pass
        elif d['status'] == 'finished':
            progress_bar.progress(1.0, text="Đang xử lý...")

    ydl_opts_base['progress_hooks'] = [hook]

    with yt_dlp.YoutubeDL(ydl_opts_base) as ydl:
        info = ydl.extract_info(url, download=True)
        # Tìm file đã tải
        files = os.listdir(temp_dir)
        if not files:
            raise Exception("Không tìm thấy file sau khi tải")
        filepath = os.path.join(temp_dir, files[0])
        return filepath, info

# --- UI ---
url = st.text_input("🔗 Dán link TikTok:", placeholder="https://www.tiktok.com/@.../video/...")

mode = st.radio("Chọn chế độ:", ["Video (Không logo)", "Âm thanh MP3"], horizontal=True)

if url:
    if not is_valid_tiktok_url(url):
        st.error("Link phải chứa tiktok.com")
    else:
        st.divider()
        if st.button(f"🚀 TẢI NGAY {mode.upper()}", use_container_width=True, type="primary"):
            progress = st.progress(0, text="Bắt đầu...")
            filepath = None
            info_title = "tiktok_video"
            mime = "video/mp4" if "Video" in mode else "audio/mpeg"
            ext = "mp4" if "Video" in mode else "mp3"

            try:
                # Thử cách 1: yt-dlp
                with st.spinner("Đang thử tải bằng yt-dlp..."):
                    filepath, info = download_with_ytdlp(url, mode, progress)
                    info_title = info.get('title', 'tiktok_video')
                    st.success("Tải bằng yt-dlp thành công!")

            except Exception as e:
                st.warning(f"yt-dlp lỗi: {e} -> Đang thử cách 2 (API dự phòng)...")
                try:
                    api_data = download_via_tikwm_api(url)
                    if api_data:
                        info_title = api_data.get('title','tiktok')
                        st.image(api_data.get('thumbnail'), caption=info_title, width=300)
                        target_url = api_data['video_url'] if "Video" in mode else api_data['music_url']
                        progress.progress(0.5, text="Đang tải file từ API...")
                        filepath = download_file_from_url(target_url)
                        progress.progress(1.0, text="Xong!")
                        st.success("Tải bằng API dự phòng thành công!")
                    else:
                        raise Exception("API cũng không lấy được link")
                except Exception as e2:
                    st.error(f"Thất bại cả 2 cách: {e2}")
                    st.info("Mẹo: TikTok chặn IP của Streamlit Cloud. Hãy thử lại sau 1 phút hoặc deploy trên Hugging Face.")
                    filepath = None

            if filepath and os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    file_bytes = f.read()
                
                safe_title = re.sub(r'[\\/*?:"<>|]', "", info_title)[:40]
                st.download_button(
                    label=f"⬇️ LƯU FILE {ext.upper()} VỀ MÁY",
                    data=file_bytes,
                    file_name=f"{safe_title}.{ext}",
                    mime=mime,
                    use_container_width=True
                )

st.markdown("---")
st.markdown("""
### Fix lỗi Streamlit Cloud thế nào?
Nếu bạn deploy trên Streamlit Cloud, bắt buộc phải tạo thêm 2 file:

**1. File `packages.txt`** (để cài ffmpeg):
```
ffmpeg
```

**2. File `requirements.txt`** (nội dung này):
```
streamlit
yt-dlp
requests
```

Sau đó reboot app là hết lỗi 100%.
""")
