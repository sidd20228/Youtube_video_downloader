import streamlit as st
import yt_dlp
import os
import uuid

st.title("YouTube Video Downloader")

url = st.text_input("Enter YouTube URL:")

def get_formats(url):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec', 'none') != 'none' and f.get('ext') == 'mp4':
                    has_audio = f.get('acodec', 'none') != 'none'
                    label = f"{f.get('format_note') or f.get('height', '')}p | {f.get('format')} | {'Audio' if has_audio else 'No Audio'}"
                    formats.append({
                        'format_id': f['format_id'],
                        'label': label,
                        'has_audio': has_audio
                    })
            return formats
    except Exception as e:
        st.error(f"Error: {e}")
        return []

if url:
    formats = get_formats(url)
    if formats:
        format_labels = [f["label"] for f in formats]
        selected = st.selectbox("Select format:", format_labels)
        selected_format = formats[format_labels.index(selected)]
        if st.button("Download"):
            video_id = str(uuid.uuid4())
            output_path = f"{video_id}.mp4"
            ydl_format = f"{selected_format['format_id']}+bestaudio[ext=m4a]/best"
            ydl_opts = {
                'format': ydl_format,
                'outtmpl': output_path,
                'quiet': True,
                'merge_output_format': 'mp4',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
                }
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="Click to Download MP4",
                        data=f,
                        file_name="video.mp4",
                        mime="video/mp4"
                    )
                os.remove(output_path)
            except Exception as e:
                st.error(f"Download failed: {e}")
    else:
        st.info("No downloadable formats found or invalid URL.")