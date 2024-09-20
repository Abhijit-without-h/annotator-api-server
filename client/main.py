import requests
import base64
import json
import uuid
import os
import tkinter as tk
from tkinter import filedialog, messagebox

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
    if audio_id is None:
        # Fetch a list of existing audio IDs
        response = requests.get(f'{BASE_URL}/list-audio')
        audio_ids = response.json().get('ids', [])
        
        if audio_ids:
            audio_id = audio_ids[0]  # Use the first available ID
        else:
            audio_id = str(uuid.uuid4())
            print(f"No existing audio IDs found. Generated new ID: {audio_id}")
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

def process_files(file_paths):
    results = []
    for file_path in file_paths:
        audio_id = submit_audio(file_path)
        fetched_data = fetch_audio(audio_id)
        results.append({'file': os.path.basename(file_path), 'id': audio_id, 'data': fetched_data})
    return results

class AudioProcessorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Audio Processor")
        master.geometry("400x300")

        self.label = tk.Label(master, text="Select audio files to process:")
        self.label.pack(pady=10)

        self.select_button = tk.Button(master, text="Select Files", command=self.select_files)
        self.select_button.pack(pady=5)

        self.process_button = tk.Button(master, text="Process Files", command=self.process_files, state=tk.DISABLED)
        self.process_button.pack(pady=5)

        self.result_text = tk.Text(master, height=10, width=50)
        self.result_text.pack(pady=10)

        self.selected_files = []

    def select_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        if file_paths:
            self.selected_files = file_paths
            self.process_button['state'] = tk.NORMAL
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Selected {len(file_paths)} file(s). Click 'Process Files' to continue.")

    def process_files(self):
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select audio files first.")
            return

        init_db()
        processed_files = process_files(self.selected_files)

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Processed files:\n")
        for result in processed_files:
            self.result_text.insert(tk.END, f"File: {result['file']}, ID: {result['id']}\n")
            sample_json = json.dumps({"filename": result['file'], "processed": True})
            save_json(result['id'], sample_json)

        self.result_text.insert(tk.END, "\nFetching updated data:\n")
        for result in processed_files:
            updated_data = fetch_audio(result['id'])
            self.result_text.insert(tk.END, f"Updated data for {result['file']}: {updated_data}\n")

        messagebox.showinfo("Processing Complete", "All files have been processed successfully.")

if __name__ == '__main__':
    root = tk.Tk()
    app = AudioProcessorGUI(root)
    root.mainloop()
