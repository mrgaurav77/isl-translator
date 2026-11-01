"""
ISL Text-to-Speech Engine
Provides thread-safe voice synthesis using pyttsx3 with rate, pitch, and voice controls.
Supports both direct PC speaker audio output and WAV streaming for web clients.
"""

import os
import threading
import queue
import time
import tempfile
import pyttsx3


class ISLTTSEngine:
    def __init__(self):
        self.speech_queue = queue.Queue()
        self.rate = 150
        self.volume = 1.0
        self.voice_id = None
        self.is_running = True

        # Discover system voices
        self.available_voices = []
        try:
            temp_eng = pyttsx3.init()
            voices = temp_eng.getProperty('voices')
            for v in voices:
                self.available_voices.append({
                    'id': v.id,
                    'name': v.name,
                    'languages': getattr(v, 'languages', [])
                })
            if self.available_voices:
                self.voice_id = self.available_voices[0]['id']
            del temp_eng
        except Exception as e:
            print(f"[ISLTTSEngine] Voice discovery note: {e}")

        # Start worker thread for background speech playback
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

    def _speech_worker(self):
        """Worker thread that executes TTS jobs sequentially without blocking the web server."""
        while self.is_running:
            try:
                task = self.speech_queue.get(timeout=1.0)
                if task is None:
                    break
                text, rate, volume, voice_id = task
                if text and text.strip():
                    try:
                        engine = pyttsx3.init()
                        if rate:
                            engine.setProperty('rate', rate)
                        if volume:
                            engine.setProperty('volume', volume)
                        if voice_id:
                            engine.setProperty('voice', voice_id)
                        engine.say(text)
                        engine.runAndWait()
                        del engine
                    except Exception as e:
                        print(f"[ISLTTSEngine] Speech error: {e}")
                self.speech_queue.task_done()
            except queue.Empty:
                continue

    def speak(self, text, rate=None, volume=None, voice_id=None):
        """Dispatches text to be spoken asynchronously."""
        if not text or not text.strip():
            return
        r = rate or self.rate
        v = volume or self.volume
        vid = voice_id or self.voice_id
        self.speech_queue.put((text.strip(), r, v, vid))

    def generate_wav(self, text, rate=None, volume=None, voice_id=None):
        """
        Generates a temporary WAV file for browser audio playback.
        Returns the path to the generated WAV file.
        """
        if not text or not text.strip():
            return None

        temp_dir = tempfile.gettempdir()
        filename = f"isl_speech_{int(time.time()*1000)}.wav"
        output_path = os.path.join(temp_dir, filename)

        try:
            engine = pyttsx3.init()
            if rate:
                engine.setProperty('rate', rate)
            if volume:
                engine.setProperty('volume', volume)
            if voice_id:
                engine.setProperty('voice', voice_id)

            engine.save_to_file(text.strip(), output_path)
            engine.runAndWait()
            del engine
            return output_path
        except Exception as e:
            print(f"[ISLTTSEngine] WAV generation error: {e}")
            return None

    def get_voices(self):
        """Returns list of available system TTS voices."""
        return self.available_voices

