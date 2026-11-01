"""
ISL Temporal Stabilizer & Story Construction Engine
Handles frame stabilization, debounces triggers, reconstructs natural sentences,
auto-detects sentence boundaries from pauses, and compiles complete continuous stories.
"""

from collections import deque, Counter
import time
from .grammar_engine import ISLGrammarEngine
from .seed_dataset import ISL_SIGNS_INFO


class ISLStabilizer:
    def __init__(self, buffer_size=8, confidence_threshold=38.0, stability_ratio=0.62,
                 repeat_delay=1.3, sentence_pause_sec=2.0):
        self.buffer_size = buffer_size
        self.confidence_threshold = confidence_threshold
        self.stability_ratio = stability_ratio
        self.repeat_delay = repeat_delay
        self.sentence_pause_sec = sentence_pause_sec # Inactivity delay to finalize sentence

        self.prediction_buffer = deque(maxlen=buffer_size)
        self.last_confirmed_sign = None
        self.last_trigger_time = 0
        self.last_activity_time = time.time()
        self.hand_present_history = deque(maxlen=6)

        # NLP Grammar Engine for natural sentences & story translation
        self.grammar = ISLGrammarEngine()

        # Speech Configuration
        # 'sentence' (speaks complete sentences), 'story' (narrate on demand), 'word' (word-by-word)
        self.speech_mode = 'sentence'

        # Current Live Word & Live Sentence state
        self.current_word = ""
        self.current_sentence_tokens = []

        # Completed Story Chronicle
        self.story_sentences = [] # list of {english, hindi, raw, timestamp}
        self.last_action_event = None

    def update(self, prediction_dict, hands_present=True):
        """
        Updates the stabilization buffer with the latest frame's prediction.
        Checks for pause-based sentence boundaries to automatically append to the story.
        """
        now = time.time()
        self.hand_present_history.append(hands_present)

        should_speak = False
        speak_text = ""
        new_token = None
        event_msg = "Standby"

        # Check if hands have rested/paused long enough to finalize active sentence into story!
        if (self.current_sentence_tokens or self.current_word) and (now - self.last_activity_time >= self.sentence_pause_sec):
            # Auto-finalize sentence into story!
            sentence_res = self.finalize_current_sentence()
            if sentence_res:
                event_msg = f"Sentence completed: '{sentence_res['english']}'"
                if self.speech_mode == 'sentence':
                    should_speak = True
                    speak_text = sentence_res['english']

        # If no hands present for several frames, reset confirmed sign
        if all(not p for p in self.hand_present_history):
            self.prediction_buffer.clear()
            self.last_confirmed_sign = None

        if not prediction_dict or not hands_present:
            return self._build_state_response(None, False, 0.0, None, should_speak, speak_text, event_msg)

        sign = prediction_dict.get('prediction')
        conf = prediction_dict.get('confidence', 0.0)

        # Filter low confidence
        if conf < self.confidence_threshold:
            return self._build_state_response(sign, False, 0.0, None, should_speak, speak_text, f"Low confidence ({conf}%)")

        self.prediction_buffer.append(sign)

        # Need full or near-full buffer before deciding stability
        if len(self.prediction_buffer) < int(self.buffer_size * 0.6):
            return self._build_state_response(sign, False, 0.0, None, should_speak, speak_text, "Tracking gesture...")

        # Find most common sign in buffer
        counts = Counter(self.prediction_buffer)
        most_common_sign, count = counts.most_common(1)[0]
        stability = (count / len(self.prediction_buffer))
        is_stable = stability >= self.stability_ratio

        if not is_stable:
            return self._build_state_response(
                most_common_sign, False, round(stability * 100, 1), None, should_speak, speak_text, "Motion detected..."
            )

        # Gesture is locked and stable! Check debounce & hold triggers
        is_different_from_last = (most_common_sign != self.last_confirmed_sign)
        time_since_last = now - self.last_trigger_time

        if is_different_from_last or (time_since_last > self.repeat_delay):
            self.last_confirmed_sign = most_common_sign
            self.last_trigger_time = now
            self.last_activity_time = now
            new_token = most_common_sign

            # Process token into words & sentences
            token_res = self._process_token(most_common_sign)
            event_msg = token_res['message']

            if self.speech_mode == 'word' and token_res['should_speak']:
                should_speak = True
                speak_text = token_res['speak_text']

        return self._build_state_response(
            most_common_sign, True, round(stability * 100, 1), new_token, should_speak, speak_text, event_msg
        )

    def _process_token(self, token):
        """Processes an accepted gesture token into words and sentences."""
        should_speak = False
        speak_text = ""
        message = ""

        # Special Action Tokens
        if token == "Space":
            if self.current_word:
                self.current_sentence_tokens.append(self.current_word)
                speak_text = self.current_word
                should_speak = True
                message = f"Word: '{self.current_word}'"
                self.current_word = ""
            else:
                message = "Space"
        elif token == "Backspace":
            if len(self.current_word) > 0:
                removed = self.current_word[-1]
                self.current_word = self.current_word[:-1]
                message = f"Deleted: '{removed}'"
            elif len(self.current_sentence_tokens) > 0:
                removed_word = self.current_sentence_tokens.pop()
                message = f"Deleted word: '{removed_word}'"
            else:
                message = "Buffer empty"
        elif token == "Stop":
            # "Stop" sign can explicitly end the current sentence!
            if self.current_word:
                self.current_sentence_tokens.append(self.current_word)
                self.current_word = ""
            self.finalize_current_sentence()
            message = "Sentence finalized with 'Stop' sign"
        elif token in ["Morning", "Afternoon", "Evening", "Night"] and self.current_sentence_tokens and self.current_sentence_tokens[-1] == "Good":
            # Compound ISLRTC greeting: Good + Morning = Good Morning
            compound = f"Good {token}"
            self.current_sentence_tokens[-1] = compound
            speak_text = compound
            should_speak = True
            message = f"Combined greeting: '{compound}'"
        elif (token in ISL_SIGNS_INFO and ISL_SIGNS_INFO[token].get("category") not in ["alphabet", "control"]) or token in ["Yes", "No"]:
            # Whole phrase/concept token: flush word first, then append phrase token
            if self.current_word:
                self.current_sentence_tokens.append(self.current_word)
                self.current_word = ""
            self.current_sentence_tokens.append(token)
            speak_text = token
            should_speak = True
            message = f"Added: '{token}'"
        else:
            # Single letter or number: append to current word
            self.current_word += token
            message = f"Typed: '{token}'"

        return {
            'should_speak': should_speak,
            'speak_text': speak_text,
            'message': message
        }

    def finalize_current_sentence(self):
        """
        Finalizes the currently assembling words into a complete, polished sentence
        and commits it into the Story Chronicle.
        """
        # Flush pending word
        if self.current_word:
            self.current_sentence_tokens.append(self.current_word)
            self.current_word = ""

        if not self.current_sentence_tokens:
            return None

        # Polish raw tokens into natural English and Hindi using Grammar Engine
        polished = self.grammar.polish_sentence(self.current_sentence_tokens)
        sentence_record = {
            "english": polished["english"],
            "hindi": polished["hindi"],
            "raw": polished["raw"],
            "tokens": list(self.current_sentence_tokens),
            "timestamp": time.strftime("%H:%M:%S")
        }

        self.story_sentences.append(sentence_record)
        self.current_sentence_tokens = []
        self.last_confirmed_sign = None
        self.last_activity_time = time.time()

        return sentence_record

    def add_space_manual(self):
        """Manually trigger space."""
        self.last_activity_time = time.time()
        if self.current_word:
            self.current_sentence_tokens.append(self.current_word)
            w = self.current_word
            self.current_word = ""
            return w
        return ""

    def backspace_manual(self):
        """Manually trigger backspace."""
        self.last_activity_time = time.time()
        if len(self.current_word) > 0:
            self.current_word = self.current_word[:-1]
        elif len(self.current_sentence_tokens) > 0:
            self.current_sentence_tokens.pop()

    def end_sentence_manual(self):
        """Manually finalize sentence and add to story."""
        return self.finalize_current_sentence()

    def clear_all(self):
        """Clears current active sentence as well as the full story."""
        self.current_word = ""
        self.current_sentence_tokens = []
        self.story_sentences = []
        self.last_confirmed_sign = None

    def get_live_sentence(self):
        """Returns the raw tokens of the current assembling sentence."""
        words = list(self.current_sentence_tokens)
        if self.current_word:
            words.append(self.current_word)
        return " ".join(words)

    def get_live_polished_preview(self):
        """Returns real-time natural language preview of the current sentence."""
        words = list(self.current_sentence_tokens)
        if self.current_word:
            words.append(self.current_word)
        if not words:
            return {"english": "", "hindi": ""}
        return self.grammar.polish_sentence(words)

    def get_story_compilation(self):
        """Compiles all finalized sentences into a flowing continuous story."""
        return self.grammar.compile_story(self.story_sentences)

    def _build_state_response(self, active_sign, is_stable, stability_pct, new_token, should_speak, speak_text, event_msg):
        story = self.get_story_compilation()
        live_preview = self.get_live_polished_preview()

        return {
            'active_sign': active_sign,
            'is_stable': is_stable,
            'stability_pct': stability_pct,
            'new_token_added': new_token,
            'should_speak': should_speak,
            'speak_text': speak_text,
            'speech_mode': self.speech_mode,

            # Live current sentence
            'current_word': self.current_word,
            'live_sentence_raw': self.get_live_sentence(),
            'live_sentence_english': live_preview['english'],
            'live_sentence_hindi': live_preview['hindi'],

            # Full Story / Narrative Chronicle
            'story_english': story['story_english'],
            'story_hindi': story['story_hindi'],
            'story_raw': story['story_raw'],
            'story_sentences': story['sentences'],
            'sentence_count': story['sentence_count'],
            'word_count': story['word_count'],
            'reading_time_seconds': story['reading_time_seconds'],

            'event_message': event_msg
        }
