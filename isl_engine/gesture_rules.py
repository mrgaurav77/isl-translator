"""
ISL Topological Landmark & Geometric Heuristic Rules Engine
Provides deterministic, high-precision recognition for Indian Sign Language gestures
matching official ISLRTC standards.
ONLY fires for unambiguous, distinctive anatomical invariants with strict geometric constraints.
Generic or ambiguous hand shapes fall through to the calibrated 220-dim Machine Learning classifier.
"""

import math
import numpy as np


def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)


def analyze_hand(landmarks):
    """
    Analyzes a 21-landmark hand.
    Returns geometric profile, finger curls, and pose signatures.
    """
    if landmarks is None or len(landmarks) < 21:
        return None

    pts = landmarks
    wrist = pts[0]
    palm_center = pts[9]
    palm_len = max(dist(wrist, palm_center), 0.001)

    # 4 Fingers extension (Index, Middle, Ring, Pinky)
    fingers = []
    for tip, pip, mcp in [(8, 6, 5), (12, 10, 9), (16, 14, 13), (20, 18, 17)]:
        rw = dist(pts[tip], wrist) / max(dist(pts[pip], wrist), 0.001)
        rm = dist(pts[tip], pts[mcp]) / max(dist(pts[pip], pts[mcp]), 0.001)
        ext = (rw > 1.25 and rm > 1.65) or (pts[tip][1] < pts[pip][1] - 0.03 and rm > 1.4)
        fingers.append(bool(ext))

    index_ext, middle_ext, ring_ext, pinky_ext = fingers

    # Thumb analysis
    thumb_vec_y = pts[4][1] - wrist[1]
    thumb_dy = pts[4][1] - pts[2][1]
    r_pinky = dist(pts[4], pts[17]) / palm_len
    thumb_ext = (r_pinky > 0.58) or (thumb_vec_y < -0.06)

    ext_list = [bool(thumb_ext), index_ext, middle_ext, ring_ext, pinky_ext]
    count = sum(ext_list)

    # Fingertips spread ratio for Food / Bunched fingertips
    spread_ratio = max(dist(pts[4], pts[i]) for i in [8, 12, 16, 20]) / palm_len
    is_bunched = (spread_ratio < 0.28) and not (count >= 4 and spread_ratio > 0.35)

    # Thumbs up / down
    is_thumbs_up = (thumb_dy < -0.04 or thumb_vec_y < -0.06) and not any(fingers) and not is_bunched
    is_thumbs_down = (thumb_dy > 0.04 or thumb_vec_y > 0.06) and not any(fingers) and not is_bunched

    # Fist
    is_fist = not any(fingers) and not is_thumbs_up and not is_bunched

    # Open Palm
    is_open = (count >= 4) and not is_bunched

    # Specific signatures
    is_v = index_ext and middle_ext and not ring_ext and not pinky_ext and not thumb_ext
    is_3 = thumb_ext and index_ext and middle_ext and not ring_ext and not pinky_ext
    is_w = index_ext and middle_ext and ring_ext and not pinky_ext and not is_open
    is_ily = thumb_ext and index_ext and not middle_ext and not ring_ext and pinky_ext
    is_y = thumb_ext and pinky_ext and not index_ext and not middle_ext and not ring_ext
    is_index = index_ext and not middle_ext and not ring_ext and not pinky_ext and not thumb_ext and not is_v and not is_w and not is_ily
    is_pinky = pinky_ext and not index_ext and not middle_ext and not ring_ext

    return {
        'fingers_extended': ext_list,
        'count': count,
        'is_fist': is_fist,
        'is_open': is_open,
        'is_thumbs_up': is_thumbs_up,
        'is_thumbs_down': is_thumbs_down,
        'is_v': is_v,
        'is_3': is_3,
        'is_w': is_w,
        'is_ily': is_ily,
        'is_y': is_y,
        'is_index': is_index,
        'is_pinky': is_pinky,
        'is_bunched': is_bunched,
        'wrist': wrist,
        'palm_center': palm_center
    }


def evaluate_isl_rules(hands_data):
    """
    Evaluates topological ISL rules across detected hands.
    Returns (sign_name, confidence, description) or None.
    ONLY fires for strict, distinctive anatomical invariants.
    """
    if hands_data is None or len(hands_data) == 0:
        return None

    left_hand = None
    right_hand = None

    for h in hands_data:
        lbl = h.get('label', 'Right')
        lms = h.get('landmarks', [])
        if lbl == 'Left' and left_hand is None:
            left_hand = lms
        elif lbl == 'Right' and right_hand is None:
            right_hand = lms

    if left_hand is None and right_hand is None and len(hands_data) > 0:
        right_hand = hands_data[0].get('landmarks', [])

    r_analysis = analyze_hand(right_hand) if right_hand is not None else None
    l_analysis = analyze_hand(left_hand) if left_hand is not None else None

    # ==================== DUAL-HAND DISTINCTIVE SIGNS ====================
    if l_analysis and r_analysis:
        lwrist = l_analysis['wrist']
        rwrist = r_analysis['wrist']
        lpalm = l_analysis['palm_center']
        rpalm = r_analysis['palm_center']
        palm_d = dist(lpalm, rpalm)

        # 1. HOME: Hands form a triangular pitched roof
        # Strict: Fingertips touch at top, wrists spread apart, fingers upright and tilted inward
        if l_analysis['is_open'] and r_analysis['is_open']:
            idx_tip_d = dist(left_hand[8], right_hand[8])
            wrist_d = dist(lwrist, rwrist)
            if idx_tip_d < 0.07 and wrist_d > 0.16 and lwrist[1] > left_hand[8][1] + 0.06 and rwrist[1] > right_hand[8][1] + 0.06:
                return ("Home", 98.5, "Home (Hands forming triangular roof)")

        # 2. NAMASTE / HELLO: Both open palms pressed together facing each other at chest
        # Strict: Palms together, wrists together, fingers pointing vertically up
        if l_analysis['count'] >= 4 and r_analysis['count'] >= 4:
            idx_tip_d = dist(left_hand[8], right_hand[8])
            wrist_d = dist(lwrist, rwrist)
            hands_upright = (left_hand[8][1] < lwrist[1] - 0.07) and (right_hand[8][1] < rwrist[1] - 0.07)
            if palm_d < 0.11 and wrist_d < 0.12 and idx_tip_d < 0.09 and hands_upright:
                return ("Namaste", 99.0, "Namaste / Hello (ISLRTC 1.2: Palms joined in greeting)")

        # 3. HELP: Right fist/thumbs-up resting directly on flat horizontal left palm
        # Strict: Left palm open facing up, right fist base touching left palm center
        if l_analysis['is_open'] and (r_analysis['is_thumbs_up'] or r_analysis['is_fist']):
            fist_on_palm_d = dist(right_hand[0], lpalm)
            if fist_on_palm_d < 0.09:
                return ("Help", 99.0, "Help (ISLRTC 1.3: Right fist resting on flat left palm)")

        # 4. DOCTOR: Right index & middle fingers tapping left inner radial wrist pulse
        if l_analysis['is_open'] and (r_analysis['is_v'] or r_analysis['count'] in [2, 3]):
            if dist(right_hand[8], lwrist) < 0.09 or dist(right_hand[12], lwrist) < 0.09:
                return ("Doctor", 99.0, "Doctor (Tapping inner wrist pulse)")

        # 5. MEDICINE: Right middle fingertip grinding into the center of left open palm
        if l_analysis['is_open'] and not r_analysis['is_open'] and not r_analysis['is_thumbs_up']:
            if dist(right_hand[12], lpalm) < 0.07:
                return ("Medicine", 98.0, "Medicine (Grinding pill on palm)")

        # 6. TIME: Right index fingertip tapping dorsal surface of left wrist
        if r_analysis['is_index'] and dist(right_hand[8], lwrist) < 0.08:
            return ("Time", 98.0, "Time (Tapping left wrist watch)")

        # 7. STAND: Right 'V' fingers standing upright on left flat palm
        if l_analysis['is_open'] and r_analysis['is_v'] and dist(right_hand[8], lpalm) < 0.09:
            return ("Stand", 98.5, "Stand (Two legs standing on palm)")

        # 8. WORK: Both closed fists tapping wrists together
        if l_analysis['is_fist'] and r_analysis['is_fist'] and dist(lwrist, rwrist) < 0.10:
            return ("Work", 98.0, "Work (Wrists tapping together)")

        # 9. NICE TO MEET YOU: Both index fingers meeting together tips touching
        if l_analysis['is_index'] and r_analysis['is_index']:
            idx_d = dist(left_hand[8], right_hand[8])
            if idx_d < 0.08:
                return ("Nice to meet you", 99.0, "Nice to meet you (ISLRTC 1.2: Index fingers meeting)")

        # 10. NUMBER 10: Both open hands with all 10 fingers extended and spread apart
        if l_analysis['count'] == 5 and r_analysis['count'] == 5 and dist(left_hand[8], right_hand[8]) > 0.18 and abs(lwrist[1] - rwrist[1]) < 0.10:
            return ("10", 97.5, "Number 10 (All 10 fingers open)")

    # ==================== SINGLE-HAND DISTINCTIVE SIGNS ====================
    active = r_analysis if r_analysis else l_analysis
    active_lms = right_hand if right_hand is not None else left_hand

    if active and active_lms is not None:
        wrist = active['wrist']

        # 1. PHONE: Y handshape (Thumb + Pinky extended, others curled) held near ear
        if (active.get('is_y', False) or active['is_ily']) and wrist[1] < 0.42:
            return ("Phone", 98.0, "Phone (Y handshape to ear)")

        # 2. I LOVE YOU: Thumb, Index, Pinky extended, Middle and Ring folded
        if active['is_ily']:
            return ("I Love You", 99.0, "I Love You (ISLRTC 2.3: Thumb, Index, Pinky extended)")

        # 3. FOOD / EAT: All 5 fingertips pinched together held near mouth
        if active['is_bunched'] and active_lms[8][1] < 0.48:
            return ("Food", 96.0, "Food / Eat (Fingertips gathered to mouth)")

        # 4. WATER: 'W' sign (Index, Middle, Ring extended; thumb holding pinky) near mouth
        if active['is_w'] and active_lms[8][1] < 0.48:
            return ("Water", 98.0, "Water (W shape near mouth)")

        # 5. NUMBER 3: Thumb, Index, Middle extended, Ring and Pinky curled
        if active.get('is_3', False) or (active['fingers_extended'][0] and active['fingers_extended'][1] and active['fingers_extended'][2] and not active['fingers_extended'][3] and not active['fingers_extended'][4]):
            return ("3", 97.0, "Number 3 (Thumb, Index, Middle extended)")

        # 6. NUMBER 4: Four fingers straight, thumb folded over palm
        if not active['fingers_extended'][0] and active['count'] == 4:
            return ("4", 97.0, "Number 4 (Four fingers extended)")

        # Note: Generic open hand, fist, and pointing are intentionally NOT caught here
        # so that the 220-dim ML classifier evaluates the true gesture (e.g. A, B, C, D, Stop, Where, Book, etc.)

    return None
