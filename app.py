from flask import Flask, request, send_file, jsonify, after_this_request
import yt_dlp
import os
import uuid

app = Flask(__name__)

@app.route('/formats', methods=['POST'])
def get_formats():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec', 'none') != 'none' and f.get('ext') == 'mp4':
                    has_audio = f.get('acodec', 'none') != 'none'
                    formats.append({
                        'format_id': f['format_id'],
                        'resolution': f.get('format_note') or f.get('height', ''),
                        'filesize': f.get('filesize') or f.get('filesize_approx'),
                        'format': f.get('format'),
                        'has_audio': has_audio
                    })
        return jsonify({'formats': formats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    format_id = data.get('format_id')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    video_id = str(uuid.uuid4())
    output_path = f"{video_id}.mp4"

    # Always merge selected video with best audio
    if format_id:
        ydl_format = f"{format_id}+bestaudio[ext=m4a]/best"
    else:
        ydl_format = 'bestvideo+bestaudio/best'

    ydl_opts = {
        'format': ydl_format,
        'outtmpl': output_path,
        'quiet': True,
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        @after_this_request
        def remove_file(response):
            try:
                os.remove(output_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
            return response

        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 