from flask import Flask, render_template, request, jsonify, send_file
import os, uuid, re
from yt_dlp import YoutubeDL

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = sanitize_filename(info.get('title', str(uuid.uuid4())))
            filename = f"{title}.mp3"
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        return jsonify({
            'title': title,
            'duration': info.get('duration'),
            'thumbnail': info.get('thumbnail'),
            'file_url': f"/file/{filename}"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/file/<filename>')
def serve_file(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run()
