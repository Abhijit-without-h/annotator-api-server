from flask import Flask, request, jsonify
import sqlite3
import os
import uuid
import base64

app = Flask(__name__)
DATABASE = 'json_data.db'
AUDIO_DIR = 'audio_files'

# Ensure audio_files directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS json_data (
                id TEXT PRIMARY KEY,
                data JSON
            )
        ''')
        conn.commit()

@app.route('/init-db', methods=['POST'])
def init_db_endpoint():
    init_db()
    return jsonify({"message": "Database initialized"}), 200

@app.route('/submit-audio', methods=['POST'])
def submit_audio():
    data = request.json
    audio_base64 = data.get('audio')
    if not audio_base64:
        return jsonify({"error": "No audio provided"}), 400

    audio_id = str(uuid.uuid4())
    audio_path = os.path.join(AUDIO_DIR, f"{audio_id}.mp3")

    with open(audio_path, "wb") as audio_file:
        audio_file.write(base64.b64decode(audio_base64))

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO json_data (id, data) VALUES (?, ?)', (audio_id, '{}'))
        conn.commit()

    return jsonify({"id": audio_id}), 200

@app.route('/fetch', methods=['POST'])
def fetch():
    data = request.json
    audio_id = data.get('id')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if audio_id:
            cursor.execute('SELECT id, data FROM json_data WHERE id = ?', (audio_id,))
        else:
            cursor.execute('SELECT id, data FROM json_data ORDER BY RANDOM() LIMIT 1')
        row = cursor.fetchone()

    if not row:
        return jsonify({"error": "No data found"}), 404

    audio_id, json_data = row
    audio_path = os.path.join(AUDIO_DIR, f"{audio_id}.mp3")

    if not os.path.exists(audio_path):
        return jsonify({"error": "Audio file not found"}), 404

    with open(audio_path, "rb") as audio_file:
        audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')

    return jsonify({"id": audio_id, "audio": audio_base64, "json": json_data}), 200

@app.route('/save-json', methods=['POST'])
def save_json():
    data = request.json
    audio_id = data.get('id')
    json_data = data.get('json_data')

    if not audio_id or not json_data:
        return jsonify({"error": "ID and JSON data are required"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE json_data SET data = ? WHERE id = ?', (json_data, audio_id))
        conn.commit()

    return jsonify({"message": "JSON data saved"}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)