"""
ISL Hand Detector & Visualizer
Processes camera frames with MediaPipe Hands to detect landmarks and render UI overlays.
"""

import cv2
import mediapipe as mp
import numpy as np


class ISLHandDetector:
    def __init__(self, max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Custom high-contrast theme colors for visualization (BGR)
        self.COLORS = {
            'Right': {
                'joint': (0, 240, 255),      # Neon Cyan / Yellow-Gold
                'joint_border': (0, 100, 180),
                'connection': (0, 220, 120), # Vivid Emerald Green
                'bbox': (0, 230, 115),
                'text_bg': (10, 80, 40)
            },
            'Left': {
                'joint': (255, 120, 220),    # Neon Pink / Magenta
                'joint_border': (150, 20, 120),
                'connection': (255, 170, 0), # Deep Amber / Orange
                'bbox': (255, 140, 0),
                'text_bg': (80, 40, 10)
            }
        }

    def process_frame(self, frame_bgr, draw_landmarks=True):
        """
        Processes a BGR image frame from webcam.
        Returns:
            annotated_frame: Frame with drawn landmarks & bounding boxes
            hands_data: List of detected hand dictionaries with normalized coordinates
        """
        h, w, c = frame_bgr.shape
        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        results = self.hands.process(frame_rgb)
        frame_rgb.flags.writeable = True

        annotated_frame = frame_bgr.copy()
        hands_data = []

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Retrieve handedness label ('Left' or 'Right')
                hand_label = "Right"
                score = 0.95
                if results.multi_handedness and idx < len(results.multi_handedness):
                    hand_info = results.multi_handedness[idx].classification[0]
                    # Note: MediaPipe assumes mirrored selfie camera by default
                    hand_label = hand_info.label
                    score = float(hand_info.score)

                # Extract 21 landmark 3D coordinates
                landmarks_list = []
                x_coords = []
                y_coords = []

                for lm in hand_landmarks.landmark:
                    landmarks_list.append((float(lm.x), float(lm.y), float(lm.z)))
                    x_coords.append(int(lm.x * w))
                    y_coords.append(int(lm.y * h))

                # Calculate bounding box
                margin = 20
                x_min = max(0, min(x_coords) - margin)
                y_min = max(0, min(y_coords) - margin)
                x_max = min(w, max(x_coords) + margin)
                y_max = min(h, max(y_coords) + margin)

                hand_dict = {
                    'label': hand_label,
                    'score': score,
                    'landmarks': landmarks_list,
                    'bbox': [x_min, y_min, x_max, y_max],
                    'center': (int((x_min + x_max) / 2), int((y_min + y_max) / 2))
                }
                hands_data.append(hand_dict)

                if draw_landmarks:
                    self._draw_custom_hand(annotated_frame, hand_landmarks, hand_dict, w, h)

        return annotated_frame, hands_data

    def _draw_custom_hand(self, frame, hand_landmarks, hand_dict, w, h):
        """Draws aesthetic cyberpunk-style hand joints and connections on the frame."""
        label = hand_dict['label']
        colors = self.COLORS.get(label, self.COLORS['Right'])

        # MediaPipe connections
        connections = self.mp_hands.HAND_CONNECTIONS

        # 1. Draw glowing connection lines
        for start_idx, end_idx in connections:
            pt1 = hand_landmarks.landmark[start_idx]
            pt2 = hand_landmarks.landmark[end_idx]
            p1 = (int(pt1.x * w), int(pt1.y * h))
            p2 = (int(pt2.x * w), int(pt2.y * h))
            # Background soft glow line
            cv2.line(frame, p1, p2, colors['connection'], 3, cv2.LINE_AA)

        # 2. Draw landmarks (circles)
        for i, lm in enumerate(hand_landmarks.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            # Fingertips are larger (indices 4, 8, 12, 16, 20)
            if i in [4, 8, 12, 16, 20]:
                cv2.circle(frame, (cx, cy), 7, colors['joint_border'], -1, cv2.LINE_AA)
                cv2.circle(frame, (cx, cy), 5, colors['joint'], -1, cv2.LINE_AA)
                cv2.circle(frame, (cx, cy), 2, (255, 255, 255), -1, cv2.LINE_AA)
            else:
                cv2.circle(frame, (cx, cy), 4, colors['joint_border'], -1, cv2.LINE_AA)
                cv2.circle(frame, (cx, cy), 3, colors['joint'], -1, cv2.LINE_AA)

        # 3. Draw Bounding Box with styled corner accents
        bbox = hand_dict['bbox']
        x1, y1, x2, y2 = bbox
        corner_len = 15

        # Thin box outline
        cv2.rectangle(frame, (x1, y1), (x2, y2), colors['bbox'], 1, cv2.LINE_AA)

        # Thick corner brackets
        t = 2
        c = colors['bbox']
        # Top-left
        cv2.line(frame, (x1, y1), (x1 + corner_len, y1), c, t)
        cv2.line(frame, (x1, y1), (x1, y1 + corner_len), c, t)
        # Top-right
        cv2.line(frame, (x2, y1), (x2 - corner_len, y1), c, t)
        cv2.line(frame, (x2, y1), (x2, y1 + corner_len), c, t)
        # Bottom-left
        cv2.line(frame, (x1, y2), (x1 + corner_len, y2), c, t)
        cv2.line(frame, (x1, y2), (x1, y2 - corner_len), c, t)
        # Bottom-right
        cv2.line(frame, (x2, y2), (x2 - corner_len, y2), c, t)
        cv2.line(frame, (x2, y2), (x2, y2 - corner_len), c, t)

        # Hand tag badge
        tag = f"{label} ({int(hand_dict['score'] * 100)}%)"
        (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        tag_y1 = max(0, y1 - 22)
        tag_y2 = tag_y1 + 20
        cv2.rectangle(frame, (x1, tag_y1), (x1 + tw + 10, tag_y2), colors['text_bg'], -1)
        cv2.rectangle(frame, (x1, tag_y1), (x1 + tw + 10, tag_y2), colors['bbox'], 1)
        cv2.putText(frame, tag, (x1 + 5, tag_y2 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

