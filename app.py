"""
Indian Sign Language (ISL) Translation Web Application
Real-Time Camera & Video File Translation into Natural Sentences & Complete Stories (Text & Voice)
Specialized for ISLRTC Module 1.2 "Greetings & Salutations in Indian Sign Language"
Flask Backend with MediaPipe, NLP Grammar Engine, and Multi-Voice TTS
"""

import os
import cv2
import json
import time
import base64
import tempfile
import numpy as np
import threading
from flask import Flask, render_template, Response, request, jsonify, send_file, session
from werkzeug.utils import secure_filename

from isl_engine.detector import ISLHandDetector
from isl_engine.model import ISLModelManager
from isl_engine.stabilizer import ISLStabilizer
from isl_engine.grammar_engine import ISLGrammarEngine
from isl_engine.tts_engine import ISLTTSEngine
from isl_engine.db import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'isl-translator-deepmind-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(tempfile.gettempdir(), 'isl_uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Core AI & NLP Components
detector = ISLHandDetector(max_num_hands=2, min_detection_confidence=0.55, min_tracking_confidence=0.5)
model_manager = ISLModelManager(model_path="models/isl_model.pkl", labels_path="models/isl_labels.json")
stabilizer = ISLStabilizer(buffer_size=8, confidence_threshold=38.0, stability_ratio=0.62, repeat_delay=1.3, sentence_pause_sec=2.0)
grammar_engine = ISLGrammarEngine()
tts_engine = ISLTTSEngine()

# Global Camera Stream State
class CameraStream:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.is_active = False
        self.lock = threading.Lock()
        self.current_frame = None
        self.last_prediction = None
        self.last_stabilized_state = {}
        self.fps = 0.0
        self.frame_count = 0
        self.start_time = time.time()
        self.mirror = True
        self.auto_speak = True

        self.start_camera()

    def start_camera(self):
        with self.lock:
            try:
                self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.camera_index)
                if self.cap.isOpened():
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.is_active = True
                    print(f"[CameraStream] Camera {self.camera_index} opened successfully.")
                else:
                    print(f"[CameraStream] Warning: Camera {self.camera_index} could not be opened. Fallback available.")
                    self.is_active = False
            except Exception as e:
                print(f"[CameraStream] Camera error: {e}")
                self.is_active = False

    def stop_camera(self):
        with self.lock:
            self.is_active = False
            if self.cap and self.cap.isOpened():
                self.cap.release()
                self.cap = None

    def switch_camera(self, new_index):
        self.stop_camera()
        self.camera_index = new_index
        self.start_camera()
        return self.is_active

    def get_frame(self):
        try:
            with self.lock:
                if not self.is_active or self.cap is None or not self.cap.isOpened():
                    frame = self._generate_standby_frame()
                    hands_data = []
                else:
                    ret, frame = self.cap.read()
                    if not ret or frame is None:
                        frame = self._generate_standby_frame()
                        hands_data = []
                    else:
                        if self.mirror:
                            frame = cv2.flip(frame, 1)
                        frame, hands_data = detector.process_frame(frame, draw_landmarks=True)

            # AI Gesture Classification
            pred_dict = None
            if hands_data and len(hands_data) > 0:
                pred_dict = model_manager.predict(hands_data)

            # Temporal Stabilization & Story Narrative Builder
            stabilized = stabilizer.update(pred_dict, hands_present=len(hands_data) > 0)
            self.last_prediction = pred_dict
            self.last_stabilized_state = stabilized

            # Auto-TTS trigger when complete sentence is formed
            if self.auto_speak and stabilized.get('should_speak') and stabilized.get('speak_text'):
                tts_engine.speak(stabilized['speak_text'])

            # FPS calculation
            self.frame_count += 1
            elapsed = time.time() - self.start_time
            if elapsed >= 1.0:
                self.fps = round(self.frame_count / elapsed, 1)
                self.frame_count = 0
                self.start_time = time.time()

            self._draw_hud(frame, len(hands_data), pred_dict, stabilized)

            ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            return jpeg.tobytes() if ret else b''
        except Exception as e:
            print(f"[CameraStream] Frame processing error: {e}")
            standby = self._generate_standby_frame()
            ret, jpeg = cv2.imencode('.jpg', standby, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            return jpeg.tobytes() if ret else b''

    def _draw_hud(self, frame, hands_count, pred_dict, stabilized):
        h, w, _ = frame.shape

        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 40), (15, 23, 42), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        status_text = f"FPS: {self.fps} | Hands: {hands_count}/2"
        cv2.putText(frame, status_text, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 240, 255), 1, cv2.LINE_AA)

        mode_text = f"Story Sentences: {stabilized.get('sentence_count', 0)}"
        cv2.putText(frame, mode_text, (w - 230, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 255, 180), 1, cv2.LINE_AA)

        if pred_dict and hands_count > 0:
            pred = pred_dict.get('prediction', '')
            conf = pred_dict.get('confidence', 0.0)
            is_stable = stabilized.get('is_stable', False)

            card_h = 60
            card_y = h - card_h - 15
            card_w = min(400, w - 40)
            card_x = int((w - card_w) / 2)

            overlay2 = frame.copy()
            cv2.rectangle(overlay2, (card_x, card_y), (card_x + card_w, card_y + card_h), (20, 20, 30), -1)
            cv2.addWeighted(overlay2, 0.85, frame, 0.15, 0, frame)

            b_color = (0, 230, 115) if is_stable else (0, 200, 255)
            cv2.rectangle(frame, (card_x, card_y), (card_x + card_w, card_y + card_h), b_color, 2, cv2.LINE_AA)

            cv2.putText(frame, f"Sign: {pred}", (card_x + 15, card_y + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

            conf_str = f"Confidence: {conf}% {'[LOCKED]' if is_stable else '[TRACKING]'}"
            cv2.putText(frame, conf_str, (card_x + 15, card_y + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, b_color, 1, cv2.LINE_AA)

    def _generate_standby_frame(self):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        for y in range(480):
            ratio = y / 480.0
            img[y, :] = [int(30 + 15 * ratio), int(18 + 10 * ratio), int(15 + 8 * ratio)]

        cv2.circle(img, (320, 220), 100, (45, 45, 70), 1, cv2.LINE_AA)
        cv2.putText(img, "ISL STORY TRANSLATOR", (160, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 230, 150), 2, cv2.LINE_AA)
        cv2.putText(img, "Camera Standby - Click 'Toggle Cam' or use Browser Camera", (100, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 220), 1, cv2.LINE_AA)
        cv2.putText(img, "Sign sentences naturally - pauses auto-complete sentences into stories", (80, 280),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (150, 160, 180), 1, cv2.LINE_AA)
        return img


camera_stream = CameraStream(camera_index=0)


# ===================== WEB ROUTES =====================

@app.route('/')
def index():
    return render_template('index.html')


def gen_frames():
    while True:
        try:
            frame_bytes = camera_stream.get_frame()
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"[gen_frames] Stream loop exception: {e}")
        time.sleep(0.03)


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/status', methods=['GET'])
def get_status():
    pred = camera_stream.last_prediction
    stabilized = camera_stream.last_stabilized_state or {}

    return jsonify({
        'camera_active': camera_stream.is_active,
        'fps': camera_stream.fps,
        'prediction': pred.get('prediction') if pred else None,
        'confidence': pred.get('confidence') if pred else 0.0,
        'top_k': pred.get('top_k') if pred else [],
        'desc': pred.get('desc') if pred else "",
        'is_stable': stabilized.get('is_stable', False),
        'stability_pct': stabilized.get('stability_pct', 0.0),

        # Current Live Sentence
        'current_word': stabilized.get('current_word', ''),
        'live_sentence_raw': stabilized.get('live_sentence_raw', ''),
        'live_sentence_english': stabilized.get('live_sentence_english', ''),
        'live_sentence_hindi': stabilized.get('live_sentence_hindi', ''),

        # Complete Story / Narrative State
        'story_english': stabilized.get('story_english', ''),
        'story_hindi': stabilized.get('story_hindi', ''),
        'story_raw': stabilized.get('story_raw', ''),
        'story_sentences': stabilized.get('story_sentences', []),
        'sentence_count': stabilized.get('sentence_count', 0),
        'word_count': stabilized.get('word_count', 0),
        'reading_time_seconds': stabilized.get('reading_time_seconds', 0),

        'speech_mode': stabilized.get('speech_mode', 'sentence'),
        'event_message': stabilized.get('event_message', ''),
        'auto_speak': camera_stream.auto_speak
    })


@app.route('/api/process_frame', methods=['POST'])
def process_browser_frame():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data'}), 400

    try:
        header, encoded = data['image'].split(',', 1) if ',' in data['image'] else ('', data['image'])
        img_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({'error': 'Failed to decode image'}), 400

        if data.get('mirror', True):
            frame = cv2.flip(frame, 1)

        annotated_frame, hands_data = detector.process_frame(frame, draw_landmarks=True)

        pred_dict = None
        if hands_data and len(hands_data) > 0:
            pred_dict = model_manager.predict(hands_data)

        stabilized = stabilizer.update(pred_dict, hands_present=len(hands_data) > 0)

        should_speak = stabilized.get('should_speak', False)
        speak_text = stabilized.get('speak_text', '')
        if camera_stream.auto_speak and should_speak and speak_text:
            tts_engine.speak(speak_text)

        _, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        annotated_b64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'success': True,
            'hands_count': len(hands_data),
            'hands_data': hands_data,
            'prediction': pred_dict,
            'stabilized': stabilized,
            'annotated_image': annotated_b64,
            'should_speak': should_speak,
            'speak_text': speak_text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== VIDEO FILE UPLOAD & TRANSLATION =====================

@app.route('/api/video/upload_translate', methods=['POST'])
def upload_translate_video():
    """
    Translates an uploaded video file (MP4/WebM/AVI/MOV) frame-by-frame.
    Extracts signs, reconstructs natural sentences, and returns the full story with timestamps.
    """
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{int(time.time())}_{filename}")
    file.save(save_path)

    # Temporary stabilizer instance dedicated to this video
    video_stabilizer = ISLStabilizer(buffer_size=8, confidence_threshold=38.0, stability_ratio=0.6, repeat_delay=1.2, sentence_pause_sec=1.6)

    try:
        cap = cv2.VideoCapture(save_path)
        if not cap.isOpened():
            return jsonify({'error': 'Could not open video file'}), 400

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

        # Sample every 2nd or 3rd frame for speed
        stride = 2 if total_frames > 300 else 1
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            if frame_idx % stride == 0:
                # Resize if high res to ensure fast detection
                h, w, _ = frame.shape
                if w > 640:
                    scale = 640.0 / w
                    frame = cv2.resize(frame, (640, int(h * scale)))

                _, hands_data = detector.process_frame(frame, draw_landmarks=False)
                pred_dict = None
                if hands_data and len(hands_data) > 0:
                    pred_dict = model_manager.predict(hands_data)

                video_stabilizer.update(pred_dict, hands_present=len(hands_data) > 0)

            frame_idx += 1

        cap.release()

        # Finalize any remaining words in buffer into a sentence
        video_stabilizer.finalize_current_sentence()
        story = video_stabilizer.get_story_compilation()

        # Update global stabilizer story so user sees it in the main dashboard as well
        if story['sentences']:
            stabilizer.story_sentences = story['sentences']

        # Clean up file
        try:
            os.remove(save_path)
        except Exception:
            pass

        return jsonify({
            'success': True,
            'story_english': story['story_english'],
            'story_hindi': story['story_hindi'],
            'story_raw': story['story_raw'],
            'sentences': story['sentences'],
            'sentence_count': story['sentence_count'],
            'word_count': story['word_count'],
            'reading_time_seconds': story['reading_time_seconds'],
            'processed_frames': frame_idx,
            'video_duration_sec': round(total_frames / video_fps, 1)
        })
    except Exception as e:
        return jsonify({'error': f"Video translation error: {str(e)}"}), 500


# ===================== STORY & SENTENCE CONTROL ROUTES =====================

@app.route('/api/sentence/space', methods=['POST'])
def sentence_space():
    word = stabilizer.add_space_manual()
    return jsonify({
        'success': True,
        'current_word': stabilizer.current_word,
        'live_sentence_raw': stabilizer.get_live_sentence()
    })


@app.route('/api/sentence/backspace', methods=['POST'])
def sentence_backspace():
    stabilizer.backspace_manual()
    return jsonify({
        'success': True,
        'current_word': stabilizer.current_word,
        'live_sentence_raw': stabilizer.get_live_sentence()
    })


@app.route('/api/story/end_sentence', methods=['POST'])
def story_end_sentence():
    res = stabilizer.end_sentence_manual()
    if res and camera_stream.auto_speak and stabilizer.speech_mode == 'sentence':
        tts_engine.speak(res['english'])
    return jsonify({
        'success': True,
        'finalized_sentence': res,
        'story': stabilizer.get_story_compilation()
    })


@app.route('/api/story/clear', methods=['POST'])
def story_clear():
    stabilizer.clear_all()
    return jsonify({
        'success': True,
        'message': 'Story reset successfully'
    })


@app.route('/api/story/narrate', methods=['POST'])
def story_narrate():
    data = request.json or {}
    lang = data.get('lang', 'english')
    story = stabilizer.get_story_compilation()

    text_to_read = story['story_english'] if lang == 'english' else story['story_hindi']
    if not text_to_read.strip():
        text_to_read = stabilizer.get_live_sentence()

    if not text_to_read.strip():
        return jsonify({'error': 'No story text to narrate'}), 400

    tts_engine.speak(text_to_read)
    return jsonify({'success': True, 'narrated_text': text_to_read})


@app.route('/api/story/load_sample', methods=['POST'])
def load_sample_story():
    """Loads the official ISLRTC Module 1.2 Greeting & Salutation Story for instant demonstration."""
    sample_sentences = [
        {
            "english": "Hello and Namaste, good morning to you all!",
            "hindi": "नमस्ते, आप सभी को सुप्रभात!",
            "raw": "Namaste Good Morning",
            "timestamp": "01:00:00"
        },
        {
            "english": "Welcome, you are most welcome here today! How are you doing?",
            "hindi": "आपका हार्दिक स्वागत है! आज आप कैसे हैं?",
            "raw": "Welcome How are you",
            "timestamp": "01:00:06"
        },
        {
            "english": "I am doing fine, thank you very much.",
            "hindi": "मैं बिल्कुल ठीक हूँ, बहुत-बहुत धन्यवाद।",
            "raw": "Fine Thank You",
            "timestamp": "01:00:12"
        },
        {
            "english": "My family and my mother are at home.",
            "hindi": "मेरा परिवार और मेरी माँ घर पर हैं।",
            "raw": "Mother Home Family",
            "timestamp": "01:00:18"
        },
        {
            "english": "I am thirsty, please give me some drinking water.",
            "hindi": "मुझे प्यास लगी है, कृपया मुझे पीने का पानी दीजिए।",
            "raw": "Water Thirsty Please",
            "timestamp": "01:00:24"
        },
        {
            "english": "I am going to school to study and learn with my teacher.",
            "hindi": "मैं शिक्षक के साथ पढ़ने और सीखने के लिए स्कूल जा रहा हूँ।",
            "raw": "School Go Study Teacher",
            "timestamp": "01:00:30"
        },
        {
            "english": "It is so nice to meet you! Goodbye, see you soon!",
            "hindi": "आपसे मिलकर बहुत खुशी हुई! अलविदा, फिर मिलेंगे!",
            "raw": "Nice to meet you Goodbye",
            "timestamp": "01:00:36"
        }
    ]
    stabilizer.story_sentences = sample_sentences
    return jsonify({
        'success': True,
        'story': stabilizer.get_story_compilation()
    })


# ===================== TTS & SETTINGS ROUTES =====================

@app.route('/api/tts/speak', methods=['POST'])
def tts_speak():
    data = request.json or {}
    text = data.get('text', '').strip()
    if not text:
        text = stabilizer.get_story_compilation()['story_english']

    if not text:
        return jsonify({'error': 'No text to speak'}), 400

    rate = int(data.get('rate', 150))
    volume = float(data.get('volume', 1.0))
    voice_id = data.get('voice_id')

    tts_engine.speak(text, rate=rate, volume=volume, voice_id=voice_id)
    return jsonify({'success': True, 'spoken_text': text})


@app.route('/api/settings/speech_mode', methods=['POST'])
def set_speech_mode():
    data = request.json or {}
    mode = data.get('mode', 'sentence')
    if mode in ['sentence', 'story', 'word']:
        stabilizer.speech_mode = mode
    return jsonify({'speech_mode': stabilizer.speech_mode})


@app.route('/api/settings/auto_speak', methods=['POST'])
def toggle_auto_speak():
    data = request.json or {}
    enabled = data.get('enabled')
    if enabled is not None:
        camera_stream.auto_speak = bool(enabled)
    else:
        camera_stream.auto_speak = not camera_stream.auto_speak
    return jsonify({'auto_speak': camera_stream.auto_speak})


@app.route('/api/camera/toggle', methods=['POST'])
def toggle_camera():
    if camera_stream.is_active:
        camera_stream.stop_camera()
    else:
        camera_stream.start_camera()
    return jsonify({'camera_active': camera_stream.is_active})


# ===================== USER AUTHENTICATION & MONGODB STORIES =====================

@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'logged_in': False, 'user': None})
    user = db.get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({'logged_in': False, 'user': None})
    return jsonify({'logged_in': True, 'user': user})


@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    res = db.register_user(username, password, email)
    if res.get('success'):
        session['user_id'] = res['user_id']
        session['username'] = res['username']
    return jsonify(res)


@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    res = db.authenticate_user(username, password)
    if res.get('success'):
        session['user_id'] = res['user_id']
        session['username'] = res['username']
    return jsonify(res)


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})


@app.route('/api/stories/save', methods=['POST'])
def save_current_story():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Please log in or register to save your stories to the database.'}), 401

    username = session.get('username', 'User')
    data = request.json or {}
    title = data.get('title', '')
    story_compilation = stabilizer.get_story_compilation()

    if not story_compilation.get('story_english') and not story_compilation.get('story_hindi'):
        return jsonify({'success': False, 'error': 'The current story is empty. Perform gestures first to build a story.'}), 400

    res = db.save_story(user_id, username, title, story_compilation)
    return jsonify(res)


@app.route('/api/stories/list', methods=['GET'])
def list_user_stories():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'stories': [], 'error': 'Please log in to view your saved stories.'}), 401

    stories = db.get_user_stories(user_id)
    return jsonify({'success': True, 'stories': stories, 'count': len(stories)})


@app.route('/api/stories/load/<story_id>', methods=['POST'])
def load_saved_story(story_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Please log in.'}), 401

    story = db.get_story(story_id, user_id)
    if not story:
        return jsonify({'success': False, 'error': 'Story not found.'}), 404

    stabilizer.story_sentences = story.get('sentences', [])
    return jsonify({'success': True, 'story': story})


@app.route('/api/stories/delete/<story_id>', methods=['DELETE'])
def delete_saved_story(story_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Please log in.'}), 401

    res = db.delete_story(story_id, user_id)
    return jsonify(res)


if __name__ == '__main__':
    print("\n=======================================================")
    print("   ISLRTC ISL STORY & GREETING TRANSLATOR READY!       ")
    print("   Open your browser at: http://127.0.0.1:5000         ")
    print("=======================================================\n")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
