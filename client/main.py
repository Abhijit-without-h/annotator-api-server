import requests
import base64
import json
import uuid
import os

BASE_URL = 'http://localhost:5006'

def init_db():
    response = requests.post(f'{BASE_URL}/init-db')
    print(response.json())

def submit_audio(file_path):
    with open(file_path, 'rb') as audio_file:
        audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
    
    response = requests.post(f'{BASE_URL}/submit-audio', json={'audio': audio_base64})
    data = response.json()
    print(f"Submitted audio: {file_path}")
    print(data)
    return data.get('id')

def fetch_audio(audio_id=None):
    payload = {'id': audio_id} if audio_id else {}
    response = requests.post(f'{BASE_URL}/fetch', json=payload)
    data = response.json()
    print(f"Fetched audio data for ID: {audio_id}")
    print(data)
    return data

def save_json(audio_id, json_data):
    response = requests.post(f'{BASE_URL}/save-json', json={'id': audio_id, 'json_data': json_data})
    print(f"Saved JSON data for ID: {audio_id}")
    print(response.json())

def process_folder(folder_path):
    audio_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp3', '.wav', '.ogg'))]
    results = []

    for audio_file in audio_files:
        file_path = os.path.join(folder_path, audio_file)
        audio_id = submit_audio(file_path)
        fetched_data = fetch_audio(audio_id)
        results.append({'file': audio_file, 'id': audio_id, 'data': fetched_data})

    return results

if __name__ == '__main__':
    # Initialize the database
    init_db()

    # Process audio files in a folder
    folder_path = '/Users/abhijitsr/Desktop/audio-file' # Replace with the actual path to your audio folder
    processed_files = process_folder(folder_path)

    # Print results
    print("\nProcessed files:")
    for result in processed_files:
        print(f"File: {result['file']}, ID: {result['id']}")

    # Optionally, you can save some JSON data for each processed file
    for result in processed_files:
        sample_json = json.dumps({"filename": result['file'], "processed": True})
        save_json(result['id'], sample_json)

    # Fetch the updated audio and JSON data for each file
    print("\nFetching updated data:")
    for result in processed_files:
        fetch_audio(result['id'])
