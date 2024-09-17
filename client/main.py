import requests
import base64
import json
import uuid

BASE_URL = 'http://localhost:5000'

def init_db():
    response = requests.post(f'{BASE_URL}/init-db')
    print(response.json())

def submit_audio(file_path):
    with open(file_path, 'rb') as audio_file:
        audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
    
    response = requests.post(f'{BASE_URL}/submit-audio', json={'audio': audio_base64})
    data = response.json()
    print(data)
    return data.get('id')

def fetch_audio(audio_id=None):
    payload = {'id': audio_id} if audio_id else {}
    response = requests.post(f'{BASE_URL}/fetch', json=payload)
    data = response.json()
    print(data)
    return data

def save_json(audio_id, json_data):
    response = requests.post(f'{BASE_URL}/save-json', json={'id': audio_id, 'json_data': json_data})
    print(response.json())

if __name__ == '__main__':
    # Initialize the database
    init_db()

    # Submit an audio file
    audio_id = submit_audio('sample.mp3')

    # Fetch the audio and JSON data
    fetched_data = fetch_audio(audio_id)

    # Save JSON data for the given ID
    sample_json = json.dumps({"example_key": "example_value"})
    
    save_json(audio_id, sample_json)

    # Fetch the updated audio and JSON data
    fetch_audio(audio_id)