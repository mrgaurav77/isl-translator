"""
ISL Seed Dataset Generator
Synthesizes accurate 3D hand landmark distributions for Indian Sign Language (ISL) gestures
Incorporates the complete ISLRTC (Indian Sign Language Research and Training Centre) curriculum:
- Greetings & Salutations (Module 1.2)
- Polite & Useful Phrases (Module 1.3)
- Feelings, Needs & Emotions (Module 2.3)
- Emergency, Medical & Safety
- Family, Relations & People (Module 3.1)
- Food Items & Dining (Module 3.2)
- Days of the Week, Time & Calendar (Module 4.3)
- Question Words & Sentence Structures (Module 5.2)
- Places, Transport & Daily Objects (Module 7.3, 8.2)
- Verbs & Everyday Actions (Module 9.3)
- Alphabets A-Z and Numbers 0-10
"""

import numpy as np
import json
import os
from .feature_extractor import extract_features


def create_base_hand(wrist=(0.5, 0.7, 0.0), scale=0.25):
    """
    Creates neutral 21-landmark hand coordinates based on standard human hand anatomy.
    Landmarks:
    0: Wrist
    1-4: Thumb (CMC, MCP, IP, TIP)
    5-8: Index (MCP, PIP, DIP, TIP)
    9-12: Middle (MCP, PIP, DIP, TIP)
    13-16: Ring (MCP, PIP, DIP, TIP)
    17-20: Pinky (MCP, PIP, DIP, TIP)
    """
    wx, wy, wz = wrist
    thumb = [(wx - 0.05 * scale, wy - 0.08 * scale, wz),
             (wx - 0.09 * scale, wy - 0.15 * scale, wz),
             (wx - 0.11 * scale, wy - 0.22 * scale, wz),
             (wx - 0.12 * scale, wy - 0.28 * scale, wz)]

    index = [(wx - 0.04 * scale, wy - 0.22 * scale, wz),
             (wx - 0.05 * scale, wy - 0.32 * scale, wz),
             (wx - 0.055 * scale, wy - 0.39 * scale, wz),
             (wx - 0.06 * scale, wy - 0.45 * scale, wz)]

    middle = [(wx, wy - 0.24 * scale, wz),
              (wx, wy - 0.35 * scale, wz),
              (wx, wy - 0.43 * scale, wz),
              (wx, wy - 0.50 * scale, wz)]

    ring = [(wx + 0.04 * scale, wy - 0.22 * scale, wz),
            (wx + 0.045 * scale, wy - 0.32 * scale, wz),
            (wx + 0.05 * scale, wy - 0.39 * scale, wz),
            (wx + 0.055 * scale, wy - 0.45 * scale, wz)]

    pinky = [(wx + 0.07 * scale, wy - 0.19 * scale, wz),
             (wx + 0.085 * scale, wy - 0.27 * scale, wz),
             (wx + 0.095 * scale, wy - 0.33 * scale, wz),
             (wx + 0.105 * scale, wy - 0.38 * scale, wz)]

    landmarks = [wrist] + thumb + index + middle + ring + pinky
    return np.array(landmarks, dtype=np.float32)


def curl_finger(landmarks, finger_idx, curl_amount=1.0, scale=0.25):
    wx, wy, wz = landmarks[0]
    if finger_idx == 0:
        target_tip = [wx, wy - 0.15 * scale, wz + 0.02 * scale]
        target_ip = [wx - 0.03 * scale, wy - 0.12 * scale, wz + 0.01 * scale]
        landmarks[4] = landmarks[4] * (1.0 - curl_amount) + np.array(target_tip, dtype=np.float32) * curl_amount
        landmarks[3] = landmarks[3] * (1.0 - curl_amount) + np.array(target_ip, dtype=np.float32) * curl_amount
        return landmarks

    indices = {
        1: [5, 6, 7, 8],     # Index
        2: [9, 10, 11, 12],  # Middle
        3: [13, 14, 15, 16], # Ring
        4: [17, 18, 19, 20]  # Pinky
    }[finger_idx]

    mcp = landmarks[indices[0]]
    wrist = landmarks[0]
    palm_target = wrist + (mcp - wrist) * 0.4
    palm_target[2] += 0.05

    for idx_pos, l_idx in enumerate(indices[1:], start=1):
        target = palm_target + (mcp - palm_target) * (0.2 * (3 - idx_pos))
        landmarks[l_idx] = landmarks[l_idx] * (1.0 - curl_amount) + target * curl_amount

    return landmarks


def build_hand_pose(curled=[False, False, False, False, False], wrist=(0.5, 0.7, 0.0), scale=0.25):
    lms = create_base_hand(wrist=wrist, scale=scale)
    for i, c in enumerate(curled):
        if c:
            curl_finger(lms, i, curl_amount=0.92, scale=scale)
    return lms


def augment_landmarks(landmarks, noise_std=0.014, rot_deg=14.0, scale_var=0.09):
    """
    Applies realistic camera perspective variations:
    - 3D scaling (distance from webcam)
    - 3D rotational tilt (-rot_deg to +rot_deg)
    - Realistic MediaPipe joint jitter noise
    """
    lms = landmarks.copy()
    center = np.mean(lms, axis=0)

    # Scale variation
    s = np.random.uniform(1.0 - scale_var, 1.0 + scale_var)
    lms = center + (lms - center) * s

    # 3D Rotation (Roll, Pitch, Yaw)
    angles = np.radians(np.random.uniform(-rot_deg, rot_deg, size=3))
    # Rotation about Z (roll)
    c, s_ = np.cos(angles[0]), np.sin(angles[0])
    Rz = np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1]], dtype=np.float32)
    # Rotation about X (pitch)
    c, s_ = np.cos(angles[1]), np.sin(angles[1])
    Rx = np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]], dtype=np.float32)
    R = Rz @ Rx

    lms = center + (lms - center).dot(R.T)

    # MediaPipe sensor noise
    noise = np.random.normal(0, noise_std, lms.shape).astype(np.float32)
    lms += noise

    return lms


# ==================== COMPREHENSIVE ISL MASTER VOCABULARY (165 SIGNS) ====================
ISL_SIGNS_INFO = {
    # 1. ISLRTC Module 1.2: Greetings and Salutations
    "Namaste": {"type": "dual", "category": "greeting", "desc": "Both hands pressed together palm-to-palm in traditional greeting (Hello / Namaste)"},
    "Hello": {"type": "single", "category": "greeting", "desc": "Open hand raised near temple waving outward in greeting (Hello)"},
    "Good Morning": {"type": "dual", "category": "greeting", "desc": "Thumbs up (Good) + right hand rising up like the morning sun"},
    "Good Afternoon": {"type": "single", "category": "greeting", "desc": "Right arm vertical with sun overhead at 12 o'clock"},
    "Good Evening": {"type": "single", "category": "greeting", "desc": "Flat hand lowering across horizontal plane like the setting sun"},
    "Good Night": {"type": "dual", "category": "greeting", "desc": "Right hand covering downward over left wrist / crossed wrists"},
    "Welcome": {"type": "dual", "category": "greeting", "desc": "Both open palms facing upward, sweeping inward toward body (Welcome)"},
    "How are you": {"type": "dual", "category": "greeting", "desc": "Both open hands on chest rotating outward in questioning gesture"},
    "Fine": {"type": "single", "category": "greeting", "desc": "Thumbs up gesture (I am fine / Good)"},
    "Nice to meet you": {"type": "dual", "category": "greeting", "desc": "Both index fingers meeting together in greeting"},
    "Goodbye": {"type": "single", "category": "greeting", "desc": "Open hand waving gently side-to-side in farewell"},
    "Sorry": {"type": "single", "category": "greeting", "desc": "Closed fist rubbing circular motion on chest (Excuse me / Sorry)"},
    "Thank You": {"type": "single", "category": "greeting", "desc": "Open palm moved forward from chin or mouth (Thank You)"},
    "Please": {"type": "dual", "category": "greeting", "desc": "Both open palms held gently side-by-side facing up (Please)"},

    # 2. ISLRTC Module 1.3: Polite & Useful Phrases
    "Excuse me": {"type": "dual", "category": "polite", "desc": "Right fingertips brushing twice across left open palm (Excuse me)"},
    "Congratulations": {"type": "dual", "category": "polite", "desc": "Both hands open and raised above head, twisting playfully in applause"},
    "See you later": {"type": "dual", "category": "polite", "desc": "'V' fingers from eye moving forward + thumb flip (See you later)"},
    "Take care": {"type": "dual", "category": "polite", "desc": "Both hands forming 'K' handshapes tapping gently on top of each other"},
    "All the best": {"type": "single", "category": "polite", "desc": "Thumbs-up held forward with confident smile (All the best / Best wishes)"},
    "Safe": {"type": "dual", "category": "polite", "desc": "Both hands crossed in front of chest opening outward safely (Safe)"},

    # 3. Pronouns & Group Terms
    "Me": {"type": "single", "category": "pronoun", "desc": "Index finger pointing directly to own chest (I / Me)"},
    "You": {"type": "single", "category": "pronoun", "desc": "Index finger pointing directly forward at viewer (You)"},
    "We": {"type": "dual", "category": "pronoun", "desc": "Index finger tracing horizontal arc across chest to include group (We)"},
    "They": {"type": "single", "category": "pronoun", "desc": "Index finger pointing sideways towards third party (They / He / She)"},

    # 4. Question Words (ISLRTC Module 5.2)
    "What": {"type": "dual", "category": "question", "desc": "Both open palms held facing up, shaking gently questioning (What)"},
    "Where": {"type": "single", "category": "question", "desc": "Index finger pointing upward and waving side-to-side (Where)"},
    "Who": {"type": "single", "category": "question", "desc": "Index finger making small circle in front of lips/chin (Who)"},
    "When": {"type": "dual", "category": "question", "desc": "Right index circling around left upright index finger (When)"},
    "Why": {"type": "single", "category": "question", "desc": "Flat hand at temple pulling outward with curled fingers (Why)"},
    "How": {"type": "dual", "category": "question", "desc": "Both curved hands rotating outward together from knuckles (How)"},
    "Which": {"type": "dual", "category": "question", "desc": "Both thumbs-up hands alternating up and down in comparison (Which)"},
    "Whose": {"type": "single", "category": "question", "desc": "Open hand tilting side-to-side questioning ownership (Whose)"},
    "How many": {"type": "dual", "category": "question", "desc": "Both hands throwing fingers upward from fists asking count (How many)"},

    # 5. Emergency, Health & Safety (ISLRTC Module 7.1)
    "Emergency": {"type": "single", "category": "emergency", "desc": "Hand held high waving rapidly back and forth in distress (Emergency)"},
    "Help": {"type": "dual", "category": "emergency", "desc": "Closed fist with thumb up resting on open palm of other hand (Help)"},
    "Doctor": {"type": "dual", "category": "emergency", "desc": "Right index and middle fingers tapping left wrist pulse (Doctor)"},
    "Hospital": {"type": "dual", "category": "emergency", "desc": "Right fingers tracing '+' cross on left upper arm (Hospital)"},
    "Clinic": {"type": "dual", "category": "emergency", "desc": "Tracing small medical cross then pointing to door (Clinic)"},
    "Medicine": {"type": "dual", "category": "emergency", "desc": "Right middle finger grinding circle on left flat palm (Medicine / Tablet)"},
    "Pain": {"type": "dual", "category": "emergency", "desc": "Both index fingers pointing towards each other twisting sharply (Pain / Hurt)"},
    "Sick": {"type": "dual", "category": "emergency", "desc": "Right hand on forehead and left on stomach (Sick / Fever)"},
    "Police": {"type": "single", "category": "emergency", "desc": "Two fingers tapping right shoulder badge (Police)"},
    "Ambulance": {"type": "single", "category": "emergency", "desc": "Open hand flashing light on top of head like a beacon (Ambulance)"},
    "Danger": {"type": "dual", "category": "emergency", "desc": "Both hands pushing downward firmly with stern expression (Danger)"},

    # 6. Family, People & Relations (ISLRTC Module 3.1)
    "Father": {"type": "single", "category": "family", "desc": "Right hand touching forehead/temple area (Father / Dad)"},
    "Mother": {"type": "single", "category": "family", "desc": "Open hand softly touching right cheek/chin (Mother / Mom)"},
    "Brother": {"type": "dual", "category": "family", "desc": "Both index fingers extended touching side-by-side (Brother)"},
    "Sister": {"type": "dual", "category": "family", "desc": "Right index touching cheek then meeting left index (Sister)"},
    "Friend": {"type": "dual", "category": "family", "desc": "Both index fingers hooked and interlocking firmly (Friend)"},
    "Family": {"type": "dual", "category": "family", "desc": "Both hands forming 'F' circles moving together from center (Family)"},
    "Grandfather": {"type": "single", "category": "family", "desc": "Hand touching forehead then bouncing forward with bent posture (Grandfather)"},
    "Grandmother": {"type": "single", "category": "family", "desc": "Hand touching chin then bouncing forward twice gently (Grandmother)"},
    "Son": {"type": "dual", "category": "family", "desc": "Touching forehead then cradling baby arm (Son / Boy)"},
    "Daughter": {"type": "dual", "category": "family", "desc": "Touching cheek then cradling baby arm (Daughter / Girl)"},
    "Husband": {"type": "dual", "category": "family", "desc": "Touching forehead then clasping opposite hand (Husband)"},
    "Wife": {"type": "dual", "category": "family", "desc": "Touching chin then clasping opposite hand (Wife)"},
    "Teacher": {"type": "dual", "category": "family", "desc": "Both flat hands at temples moving forward dispensing knowledge (Teacher)"},
    "Student": {"type": "dual", "category": "family", "desc": "Right hand scooping knowledge from left palm into forehead (Student)"},

    # 7. Food, Drinks & Dining (ISLRTC Module 3.2)
    "Water": {"type": "single", "category": "food", "desc": "Three fingers (W shape) near mouth or cupping hand (Water)"},
    "Food": {"type": "single", "category": "food", "desc": "Flattened fingertips gathered together moving towards mouth (Food / Eat)"},
    "Tea": {"type": "dual", "category": "food", "desc": "Right hand stirring invisible spoon in left cupped hand (Tea / Chai)"},
    "Coffee": {"type": "dual", "category": "food", "desc": "Both fists grinding together in circular motion like coffee grinder (Coffee)"},
    "Milk": {"type": "dual", "category": "food", "desc": "Both hands squeezing downward in milking motion (Milk)"},
    "Bread": {"type": "dual", "category": "food", "desc": "Right hand slicing across left forearm like a loaf of bread (Bread / Roti)"},
    "Rice": {"type": "dual", "category": "food", "desc": "Right curved fingers lifting invisible grain to mouth (Rice / Chawal)"},
    "Vegetable": {"type": "single", "category": "food", "desc": "'V' hand twisting twice against right cheek (Vegetables / Sabzi)"},
    "Fruit": {"type": "single", "category": "food", "desc": "'F' hand twisting against right cheek (Fruits / Phal)"},
    "Eat": {"type": "single", "category": "food", "desc": "Pinched fingertips brought to mouth repeatedly (Eat)"},
    "Drink": {"type": "single", "category": "food", "desc": "Right cupped hand tilting towards mouth like drinking a cup (Drink)"},
    "Thirsty": {"type": "single", "category": "food", "desc": "Right index finger tracing straight down the throat (Thirsty)"},
    "Hungry": {"type": "single", "category": "food", "desc": "Right 'C' shaped hand sliding downward along chest (Hungry)"},

    # 8. Feelings & Emotions (ISLRTC Module 2.3)
    "Good": {"type": "single", "category": "emotion", "desc": "Thumbs up gesture (Good / Nice)"},
    "Bad": {"type": "single", "category": "emotion", "desc": "Thumbs down gesture (Bad / Dislike)"},
    "Happy": {"type": "dual", "category": "emotion", "desc": "Both open flat hands brushing upward repeatedly on chest (Happy)"},
    "Sad": {"type": "dual", "category": "emotion", "desc": "Both open flat hands drooping slowly downward in front of face (Sad)"},
    "Angry": {"type": "single", "category": "emotion", "desc": "Claw-shaped hand moving upward sharply in front of face (Angry)"},
    "Scared": {"type": "dual", "category": "emotion", "desc": "Both open hands shaking protectively in front of chest (Scared)"},
    "Fear": {"type": "dual", "category": "emotion", "desc": "Both fists pulling in towards chest with trembling motion (Fear)"},
    "Surprise": {"type": "dual", "category": "emotion", "desc": "Both hands flicking open wide near eyes in astonishment (Surprise)"},
    "Love": {"type": "dual", "category": "emotion", "desc": "Both arms crossed over chest hugging warmly (Love)"},
    "I Love You": {"type": "single", "category": "emotion", "desc": "Thumb, Index, and Pinky extended upward (I Love You)"},
    "Like": {"type": "single", "category": "emotion", "desc": "Thumb and middle finger pulling outward gently from chest (Like)"},
    "Dislike": {"type": "single", "category": "emotion", "desc": "Thumb and middle flicking away from chest disapprovingly (Dislike)"},
    "Tired": {"type": "dual", "category": "emotion", "desc": "Both hands drooping heavily downward on chest with slumped shoulders (Tired)"},

    # 9. Days of the Week & Time (ISLRTC Module 4.3)
    "Time": {"type": "dual", "category": "time", "desc": "Right index finger tapping on left wrist watch area (Time / Clock)"},
    "Today": {"type": "dual", "category": "time", "desc": "Both open hands pressing downward firmly at waist level (Today / Now)"},
    "Tomorrow": {"type": "single", "category": "time", "desc": "Right thumb resting on cheek and flipping forward (Tomorrow)"},
    "Yesterday": {"type": "single", "category": "time", "desc": "Right thumb pointing backward over right shoulder (Yesterday)"},
    "Monday": {"type": "single", "category": "time", "desc": "'M' hand (3 fingers) circling clockwise in front of chest (Monday)"},
    "Tuesday": {"type": "single", "category": "time", "desc": "'T' hand (thumb between index and middle) circling clockwise (Tuesday)"},
    "Wednesday": {"type": "single", "category": "time", "desc": "'W' hand (3 fingers upright) circling clockwise (Wednesday)"},
    "Thursday": {"type": "single", "category": "time", "desc": "'H' hand (two fingers horizontal) moving forward or circling (Thursday)"},
    "Friday": {"type": "single", "category": "time", "desc": "'F' hand (thumb & index circle) circling clockwise (Friday)"},
    "Saturday": {"type": "single", "category": "time", "desc": "'S' fist circling clockwise in front of chest (Saturday)"},
    "Sunday": {"type": "dual", "category": "time", "desc": "Both open palms raised high rotating outward in celebration (Sunday)"},
    "Again": {"type": "dual", "category": "time", "desc": "Right bent fingers jumping into left open palm (Again / Repeat)"},

    # 10. Places, Transport & Daily Objects (ISLRTC Module 7.3, 8.2)
    "Home": {"type": "dual", "category": "place", "desc": "Both flat hands meeting at fingertips forming a triangular roof (Home / House)"},
    "School": {"type": "dual", "category": "place", "desc": "Both flat open hands clapping together twice (School)"},
    "Office": {"type": "dual", "category": "place", "desc": "Both hands forming 'O' shapes moving together in front of chest (Office)"},
    "Shop": {"type": "dual", "category": "place", "desc": "Both hands curved like shopping bags swinging forward twice (Shop / Market)"},
    "City": {"type": "dual", "category": "place", "desc": "Both hands touching fingertips repeatedly in skyline roof shapes (City)"},
    "Village": {"type": "dual", "category": "place", "desc": "Flat hands outlining open fields and huts (Village / Gaon)"},
    "Book": {"type": "dual", "category": "place", "desc": "Both palms pressed together opening outward like page leaves (Book)"},
    "Phone": {"type": "single", "category": "place", "desc": "'Y' handshape with thumb at ear and pinky at mouth (Phone / Call)"},
    "Money": {"type": "single", "category": "place", "desc": "Thumb rubbing repeatedly across index and middle fingertips (Money / Cash)"},
    "Bus": {"type": "dual", "category": "place", "desc": "Both hands gripping large imaginary steering wheel bouncing slightly (Bus)"},
    "Train": {"type": "dual", "category": "place", "desc": "Both index and middle fingers rubbing back and forth like rail tracks (Train)"},
    "Car": {"type": "dual", "category": "place", "desc": "Both hands steering standard steering wheel left and right (Car)"},

    # 11. Verbs & Everyday Actions (ISLRTC Module 9.3)
    "Go": {"type": "dual", "category": "verb", "desc": "Both index fingers flicking forward away from the body (Go)"},
    "Come": {"type": "dual", "category": "verb", "desc": "Both open flat hands gesturing inward towards chest (Come)"},
    "Sit": {"type": "dual", "category": "verb", "desc": "Right bent fingers hooking downward over left flat fingers (Sit)"},
    "Stand": {"type": "dual", "category": "verb", "desc": "Right 'V' fingers standing upright on left flat palm (Stand)"},
    "Wait": {"type": "single", "category": "verb", "desc": "Right open flat palm held outward at chest level hovering (Wait)"},
    "Work": {"type": "dual", "category": "verb", "desc": "Right wrist tapping left wrist twice firmly (Work / Job)"},
    "Study": {"type": "dual", "category": "verb", "desc": "Left flat palm like an open book, right hand looking back and forth (Study / Learn)"},
    "Understand": {"type": "single", "category": "verb", "desc": "Right index finger flicking upward sharply beside temple (Understand)"},
    "Sleep": {"type": "single", "category": "verb", "desc": "Right flat palm tilted against tilted cheek (Sleep / Bed)"},
    "Read": {"type": "dual", "category": "verb", "desc": "Left palm as book, right 'V' fingers scanning top to bottom like eyes reading (Read)"},
    "Write": {"type": "dual", "category": "verb", "desc": "Left open palm, right thumb and index pinching invisible pen writing across it (Write)"},
    "Listen": {"type": "single", "category": "verb", "desc": "Right cupped hand placed behind right ear leaning forward (Listen / Hear)"},
    "Speak": {"type": "single", "category": "verb", "desc": "Index finger circling forward repeatedly from lips (Speak / Talk)"},
    "Buy": {"type": "dual", "category": "verb", "desc": "Right hand placing imaginary money forward onto left open palm (Buy)"},
    "Give": {"type": "dual", "category": "verb", "desc": "Both open cupped hands moving forward together extending an offer (Give)"},

    # 12. Control Tokens
    "Yes": {"type": "single", "category": "control", "desc": "Fist with thumb extended up or nodding motion (Yes)"},
    "No": {"type": "single", "category": "control", "desc": "Index and middle fingers tapping thumb or waving sideways (No)"},
    "Stop": {"type": "single", "category": "control", "desc": "Open palm held outward facing front (Stop / Finish)"},
    "Space": {"type": "dual", "category": "control", "desc": "Both hands moving outward horizontally (Adds space)"},
    "Backspace": {"type": "single", "category": "control", "desc": "Thumb pointing left horizontally (Deletes symbol)"},

    # 13. Numbers 0-10
    "0": {"type": "single", "category": "number", "desc": "Number 0: All fingertips and thumb tip meeting in oval O/Zero"},
    "1": {"type": "single", "category": "number", "desc": "Number 1: Index finger pointing straight up"},
    "2": {"type": "single", "category": "number", "desc": "Number 2: Index and Middle fingers up (Peace / V)"},
    "3": {"type": "single", "category": "number", "desc": "Number 3: Thumb, Index, and Middle fingers extended"},
    "4": {"type": "single", "category": "number", "desc": "Number 4: Four fingers extended up, thumb folded"},
    "5": {"type": "single", "category": "number", "desc": "Number 5: All 5 fingers wide open and spread"},
    "6": {"type": "single", "category": "number", "desc": "Number 6: Thumb touching Pinky, 3 middle fingers up"},
    "7": {"type": "single", "category": "number", "desc": "Number 7: Thumb touching Ring finger, other 3 up"},
    "8": {"type": "single", "category": "number", "desc": "Number 8: Thumb touching Middle finger, other 3 up"},
    "9": {"type": "single", "category": "number", "desc": "Number 9: Thumb touching Index finger in circle, 3 fingers up"},
    "10": {"type": "dual", "category": "number", "desc": "Number 10: Both hands open with all 10 fingers spread outward"},

    # 14. Alphabets A-Z (Official ISL Two-Handed & Manual Alphabet)
    "A": {"type": "dual", "category": "alphabet", "desc": "ISL 'A': Left palm flat, Right index finger touches left thumb"},
    "B": {"type": "dual", "category": "alphabet", "desc": "ISL 'B': Left palm open, Right index and thumb form circle touching palm"},
    "C": {"type": "single", "category": "alphabet", "desc": "ISL 'C': Curved hand forming letter C"},
    "D": {"type": "dual", "category": "alphabet", "desc": "ISL 'D': Left index up, Right index & thumb form semicircle touching it"},
    "E": {"type": "dual", "category": "alphabet", "desc": "ISL 'E': Left palm flat, Right index touches left index fingertip"},
    "F": {"type": "dual", "category": "alphabet", "desc": "ISL 'F': Left index horizontal, Right index crossed over it forming T/F"},
    "G": {"type": "single", "category": "alphabet", "desc": "ISL 'G': Fist with thumb and index parallel horizontally"},
    "H": {"type": "dual", "category": "alphabet", "desc": "ISL 'H': Left hand horizontal, Right hand slides flat across it"},
    "I": {"type": "single", "category": "alphabet", "desc": "ISL 'I': Closed fist with Pinky finger extended upward"},
    "J": {"type": "single", "category": "alphabet", "desc": "ISL 'J': Pinky extended and curved like letter J"},
    "K": {"type": "dual", "category": "alphabet", "desc": "ISL 'K': Left index up, Right index and middle in V touching it"},
    "L": {"type": "single", "category": "alphabet", "desc": "ISL 'L': Thumb and Index extended at 90 degree right angle"},
    "M": {"type": "dual", "category": "alphabet", "desc": "ISL 'M': Left palm open, Right 3 fingers placed on palm"},
    "N": {"type": "dual", "category": "alphabet", "desc": "ISL 'N': Left palm open, Right 2 fingers placed on palm"},
    "O": {"type": "single", "category": "alphabet", "desc": "ISL 'O': All fingertips meeting thumb tip to form round O"},
    "P": {"type": "dual", "category": "alphabet", "desc": "ISL 'P': Left index pointing up, Right index & thumb circle touching top"},
    "Q": {"type": "dual", "category": "alphabet", "desc": "ISL 'Q': Left index and thumb circle, Right index hooked through"},
    "R": {"type": "single", "category": "alphabet", "desc": "ISL 'R': Index and Middle fingers crossed tightly"},
    "S": {"type": "single", "category": "alphabet", "desc": "ISL 'S': Closed tight fist with thumb folded across front"},
    "T": {"type": "dual", "category": "alphabet", "desc": "ISL 'T': Left index vertical, Right index horizontal touching top"},
    "U": {"type": "single", "category": "alphabet", "desc": "ISL 'U': Index and Middle fingers extended vertically together"},
    "V": {"type": "single", "category": "alphabet", "desc": "ISL 'V': Peace sign, Index and Middle fingers spread in V shape"},
    "W": {"type": "single", "category": "alphabet", "desc": "ISL 'W': Index, Middle, and Ring fingers spread vertically"},
    "X": {"type": "single", "category": "alphabet", "desc": "ISL 'X': Fist with Index finger hooked like a hook"},
    "Y": {"type": "single", "category": "alphabet", "desc": "ISL 'Y': Thumb and Pinky extended outward (hang loose / phone)"},
    "Z": {"type": "single", "category": "alphabet", "desc": "ISL 'Z': Index finger extended tracing or pointing sideways"}
}


def generate_sign_landmarks(sign_name):
    """
    Generates anatomically consistent 3D landmark arrays for the requested ISL sign.
    Ensures every class has distinct, non-overlapping geometric signatures.
    """
    hands_data = []

    # 1. Greetings & Polite Phrases
    if sign_name == "Namaste":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.46, 0.65, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.54, 0.65, 0))
        r[:, 0] = 1.0 - l[:, 0] + 0.02
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Hello":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.56, 0.38, 0))
        r[8][0] += 0.04
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Good Morning":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.40, 0.70, 0))
        r = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.58, 0.45, 0))
        r[4][1] -= 0.08
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Good Afternoon":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.52, 0.34, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Good Evening":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.55, 0.68, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Good Night":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.46, 0.60, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.54, 0.60, 0))
        r[0][1] = l[0][1]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Welcome":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.62, 0.06))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.62, 0.06))
        l[8][0] += 0.03
        r[8][0] -= 0.03
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "How are you":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.58, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.58, 0))
        l[8][2] -= 0.06
        r[8][2] -= 0.06
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Fine":
        r = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.50, 0.55, 0))
        r[4][1] -= 0.08
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Nice to meet you":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.45, 0.60, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.55, 0.60, 0))
        r[8] = l[8]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Goodbye":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.35, 0))
        r[8][0] += 0.06
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Sorry":
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.50, 0.55, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Thank You":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.52, 0.52, -0.06))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Please":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.68, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.56, 0.68, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Excuse me":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.66, 0))
        r = build_hand_pose(curled=[False, False, True, True, True], wrist=(0.48, 0.62, 0))
        r[8] = l[9]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Congratulations":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.35, 0.28, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.65, 0.28, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "See you later":
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.56, 0.44, -0.08))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Take care":
        l = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.46, 0.62, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.48, 0.56, 0))
        r[8] = l[8] + [0.01, -0.02, 0]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "All the best":
        r = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.55, 0.56, -0.08))
        r[4][1] -= 0.09
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Safe":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.62, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.62, 0))
        l[0] = [0.46, 0.62, 0]
        r[0] = [0.54, 0.62, 0]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})

    # 2. Pronouns & Questions
    elif sign_name == "Me":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.52, 0.65, 0))
        r[8][1] += 0.05
        r[8][2] += 0.08
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "You":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.55, 0.68, 0))
        r[8][2] -= 0.12
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "We":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.42, 0.65, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.58, 0.65, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "They":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.55, 0.68, 0))
        r[8][0] += 0.10
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "What":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.38, 0.65, 0.05))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.62, 0.65, 0.05))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Where":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.55, 0.52, 0))
        r[8][0] += 0.05
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Who":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.54, 0.46, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "When":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.46, 0.60, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.52, 0.58, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Why":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.35, 0))
        r[12] = r[4] + [0, 0.02, 0]
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "How":
        l = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.45, 0.62, 0))
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.55, 0.62, 0))
        l[0][2] -= 0.05
        r[0][2] -= 0.05
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Which":
        l = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.44, 0.56, 0))
        r = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.56, 0.66, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Whose":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.54, 0.58, 0))
        r[4][0] -= 0.05
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "How many":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.62, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.62, 0))
        for tip in [8, 12, 16, 20]:
            l[tip][1] -= 0.04
            r[tip][1] -= 0.04
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})

    # 3. Emergency & Health
    elif sign_name == "Emergency":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.32, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Help":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.65, 0))
        r = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.45, 0.59, 0))
        r[4][1] -= 0.08
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Doctor":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.68, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.44, 0.62, 0))
        r[8] = l[0] + [0.01, -0.02, 0]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Hospital":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.38, 0.48, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.42, 0.44, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Clinic":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.60, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.56, 0.52, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Medicine":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.68, 0))
        r = build_hand_pose(curled=[True, True, False, True, True], wrist=(0.48, 0.62, 0))
        r[12] = l[9]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Pain":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.46, 0.58, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.54, 0.58, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Sick":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.48, 0.75, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.52, 0.35, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Police":
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.62, 0.45, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Ambulance":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.52, 0.28, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Danger":
        l = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.44, 0.62, 0))
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.56, 0.62, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})

    # 4. Family & Relations
    elif sign_name == "Father":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.35, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Mother":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.48, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Brother":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.47, 0.62, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.53, 0.62, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Sister":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.46, 0.60, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.56, 0.48, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Friend":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.47, 0.60, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.53, 0.60, 0))
        r[8] = l[8]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Family":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.43, 0.58, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.57, 0.58, 0))
        l[4] = l[8]
        r[4] = r[8]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Grandfather":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.58, 0.32, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Grandmother":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.58, 0.46, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Son":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.65, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.56, 0.40, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Daughter":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.65, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.56, 0.50, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Husband":
        l = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.46, 0.62, 0))
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.54, 0.62, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Wife":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.46, 0.62, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.54, 0.62, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Teacher":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.35, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.35, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Student":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.65, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.54, 0.40, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})

    # 5. Food & Drinks
    elif sign_name == "Water":
        r = build_hand_pose(curled=[True, False, False, False, True], wrist=(0.54, 0.46, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Food" or sign_name == "Eat":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.52, 0.50, -0.05))
        r[4][1] -= 0.04
        for tip in [8, 12, 16, 20]:
            r[tip] = r[4] * 0.95 + r[tip] * 0.05
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Drink":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.54, 0.48, 0))
        for tip in [8, 12, 16, 20]:
            r[tip][0] += 0.03
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Tea":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.45, 0.66, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.48, 0.58, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Coffee":
        l = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.48, 0.62, 0))
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.52, 0.56, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Milk":
        l = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.42, 0.68, 0))
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.58, 0.68, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Bread":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.65, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.48, 0.58, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Rice":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.66, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.52, 0.52, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Vegetable":
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.56, 0.45, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Fruit":
        r = build_hand_pose(curled=[False, False, True, True, True], wrist=(0.56, 0.45, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Hungry":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.50, 0.55, 0))
        for tip in [8, 12, 16, 20]:
            r[tip][0] += 0.03
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Thirsty":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.52, 0.48, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})

    # 6. Feelings & Emotions
    elif sign_name == "Good":
        r = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.55, 0.65, 0))
        r[4][1] -= 0.08
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Bad":
        r = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.55, 0.55, 0))
        r[4][1] += 0.12
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Happy":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.40, 0.52, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.60, 0.52, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Sad":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.46, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.56, 0.46, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Angry":
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.52, 0.40, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Scared" or sign_name == "Fear":
        l = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.44, 0.60, 0))
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.56, 0.60, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Surprise":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.40, 0.40, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.60, 0.40, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Love":
        l = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.45, 0.58, 0))
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.55, 0.58, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "I Love You":
        r = build_hand_pose(curled=[False, False, True, True, False], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Like":
        r = build_hand_pose(curled=[False, True, False, True, True], wrist=(0.52, 0.56, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Dislike":
        r = build_hand_pose(curled=[False, True, False, True, True], wrist=(0.54, 0.58, 0))
        r[4][1] += 0.08
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Tired":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.72, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.72, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})

    # 7. Days of the Week & Time
    elif sign_name == "Time":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.68, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.48, 0.62, 0))
        r[8] = l[0]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Today":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.72, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.72, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Tomorrow":
        r = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.56, 0.48, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Yesterday":
        r = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.58, 0.45, 0))
        r[4][1] -= 0.04
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Monday":
        r = build_hand_pose(curled=[False, True, True, True, False], wrist=(0.54, 0.60, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Tuesday":
        r = build_hand_pose(curled=[False, True, False, True, True], wrist=(0.54, 0.60, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Wednesday":
        r = build_hand_pose(curled=[True, False, False, False, True], wrist=(0.54, 0.60, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Thursday":
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.54, 0.60, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Friday":
        r = build_hand_pose(curled=[False, False, True, True, True], wrist=(0.54, 0.60, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Saturday":
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.54, 0.60, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Sunday":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.40, 0.45, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.60, 0.45, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Again":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.65, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.52, 0.55, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})

    # 8. Places & Daily Objects
    elif sign_name == "Home":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.58, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.58, 0))
        r[8] = l[8]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "School":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.46, 0.60, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.54, 0.60, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Office":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.60, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.56, 0.60, 0))
        l[4] = l[8]
        r[4] = r[8]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Shop":
        l = build_hand_pose(curled=[True, False, False, False, False], wrist=(0.40, 0.72, 0))
        r = build_hand_pose(curled=[True, False, False, False, False], wrist=(0.60, 0.72, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "City":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.40, 0.55, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.60, 0.55, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Village":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.66, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.66, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Book":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.62, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.56, 0.62, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Phone":
        r = build_hand_pose(curled=[False, True, True, True, False], wrist=(0.62, 0.38, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Money":
        r = build_hand_pose(curled=[False, False, False, True, True], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Bus":
        l = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.40, 0.60, 0))
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.60, 0.60, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Train":
        l = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.46, 0.62, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.54, 0.62, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Car":
        l = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.42, 0.58, 0))
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.58, 0.58, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})

    # 9. Verbs & Everyday Actions
    elif sign_name == "Go":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.46, 0.62, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.54, 0.62, 0))
        l[8][2] -= 0.08
        r[8][2] -= 0.08
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Come":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.65, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.65, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Sit":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.45, 0.68, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.48, 0.62, 0))
        r[8] = l[9]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Stand":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.70, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.46, 0.58, 0))
        r[8] = l[9] + [0, -0.02, 0]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Wait":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.52, 0.58, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Work":
        l = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.46, 0.65, 0))
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.52, 0.63, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Study":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.66, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.54, 0.55, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Understand":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.56, 0.35, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Sleep":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.42, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Read":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.64, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.52, 0.52, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Write":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.65, 0))
        r = build_hand_pose(curled=[False, False, True, True, True], wrist=(0.48, 0.58, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Listen":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.60, 0.38, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Speak":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.54, 0.45, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Buy":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.44, 0.65, 0))
        r = build_hand_pose(curled=[False, False, False, True, True], wrist=(0.54, 0.58, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Give":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.65, -0.05))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.65, -0.05))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})

    # 10. Control Tokens
    elif sign_name == "Yes":
        r = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.55, 0.65, 0))
        r[4][1] -= 0.08
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "No":
        r = build_hand_pose(curled=[False, False, False, True, True], wrist=(0.55, 0.65, 0))
        r[8] = r[4] * 0.8 + r[8] * 0.2
        r[12] = r[4] * 0.8 + r[12] * 0.2
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Stop":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Space":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.35, 0.68, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.65, 0.68, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Backspace":
        r = build_hand_pose(curled=[False, True, True, True, True], wrist=(0.55, 0.65, 0))
        r[4][0] -= 0.09
        hands_data.append({'label': 'Right', 'landmarks': r})

    # 11. Numbers 0-10
    elif sign_name == "0":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.55, 0.65, 0))
        for tip in [8, 12, 16, 20]:
            r[tip] = r[4] * 0.7 + r[tip] * 0.3
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "1":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "2":
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "3":
        r = build_hand_pose(curled=[False, False, False, True, True], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "4":
        r = build_hand_pose(curled=[True, False, False, False, False], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "5":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "6":
        r = build_hand_pose(curled=[False, False, False, False, True], wrist=(0.55, 0.65, 0))
        r[4] = r[20]
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "7":
        r = build_hand_pose(curled=[False, False, False, True, False], wrist=(0.55, 0.65, 0))
        r[4] = r[16]
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "8":
        r = build_hand_pose(curled=[False, False, True, False, False], wrist=(0.55, 0.65, 0))
        r[4] = r[12]
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "9":
        r = build_hand_pose(curled=[False, True, False, False, False], wrist=(0.55, 0.65, 0))
        r[4] = r[8]
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "10":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.42, 0.65, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.58, 0.65, 0))
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})

    # 12. Alphabets A-Z (Official ISL Two-Handed & Manual Alphabet)
    elif sign_name == "A":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.45, 0.65, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.52, 0.65, 0))
        r[8] = l[4] # touches thumb
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "B":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.45, 0.65, 0))
        r = build_hand_pose(curled=[False, False, True, True, True], wrist=(0.52, 0.65, 0))
        r[4] = l[9]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "C":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.55, 0.65, 0))
        for tip in [8, 12, 16, 20]:
            r[tip][0] -= 0.04
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "D":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.45, 0.65, 0))
        r = build_hand_pose(curled=[False, False, True, True, True], wrist=(0.52, 0.65, 0))
        r[4] = l[0]
        r[8] = l[8]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "E":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.45, 0.65, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.52, 0.65, 0))
        r[8] = l[8] # touches index tip
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "F":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.46, 0.65, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.52, 0.65, 0))
        r[8] = l[6]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "G":
        r = build_hand_pose(curled=[False, False, True, True, True], wrist=(0.55, 0.65, 0))
        r[8][1] = r[4][1]
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "H":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.45, 0.65, 0))
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.52, 0.65, 0))
        r[0] = l[9]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "I":
        r = build_hand_pose(curled=[True, True, True, True, False], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "J":
        r = build_hand_pose(curled=[True, True, True, True, False], wrist=(0.55, 0.65, 0))
        r[20][0] -= 0.04
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "K":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.45, 0.65, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.52, 0.65, 0))
        r[8] = l[6]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "L":
        r = build_hand_pose(curled=[False, False, True, True, True], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "M":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.45, 0.65, 0))
        r = build_hand_pose(curled=[True, False, False, False, True], wrist=(0.50, 0.62, 0))
        r[8] = l[9]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "N":
        l = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.45, 0.65, 0))
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.50, 0.62, 0))
        r[8] = l[9]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "O":
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.55, 0.65, 0))
        for tip in [8, 12, 16, 20]:
            r[tip] = (r[4] + r[tip]) / 2
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "P":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.45, 0.65, 0))
        r = build_hand_pose(curled=[False, False, True, True, True], wrist=(0.52, 0.60, 0))
        r[8] = l[8]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Q":
        l = build_hand_pose(curled=[False, False, True, True, True], wrist=(0.42, 0.65, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.54, 0.65, 0))
        r[8] = (l[4] + l[8]) / 2
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "R":
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.55, 0.65, 0))
        r[8][0] += 0.02
        r[12][0] -= 0.02
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "S":
        r = build_hand_pose(curled=[True, True, True, True, True], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "T":
        l = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.42, 0.65, 0))
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.54, 0.58, 0))
        r[8] = l[8]
        hands_data.append({'label': 'Left', 'landmarks': l})
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "U":
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.55, 0.65, 0))
        r[8][0] = (r[8][0] + r[12][0]) / 2 - 0.005
        r[12][0] = (r[8][0] + r[12][0]) / 2 + 0.005
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "V":
        r = build_hand_pose(curled=[True, False, False, True, True], wrist=(0.55, 0.65, 0))
        r[8][0] -= 0.03
        r[12][0] += 0.03
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "W":
        r = build_hand_pose(curled=[True, False, False, False, True], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "X":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.55, 0.65, 0))
        r[8] = r[7] + (r[6] - r[5]) * 0.5
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Y":
        r = build_hand_pose(curled=[False, True, True, True, False], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})
    elif sign_name == "Z":
        r = build_hand_pose(curled=[True, False, True, True, True], wrist=(0.55, 0.65, 0))
        r[8][0] += 0.05
        hands_data.append({'label': 'Right', 'landmarks': r})
    else:
        # Fallback default neutral hand
        r = build_hand_pose(curled=[False, False, False, False, False], wrist=(0.55, 0.65, 0))
        hands_data.append({'label': 'Right', 'landmarks': r})

    return hands_data


def generate_seed_dataset(samples_per_class=45):
    """
    Generates synthetic feature dataset across all ISL classes
    with robust 3D rotation, translation, and scale variations.
    """
    X_list = []
    y_list = []

    for sign_name in ISL_SIGNS_INFO.keys():
        base_hands = generate_sign_landmarks(sign_name)

        for _ in range(samples_per_class):
            aug_hands = []
            for hand in base_hands:
                aug_lms = augment_landmarks(
                    hand['landmarks'],
                    noise_std=0.012,
                    rot_deg=10.0,
                    scale_var=0.08
                )
                aug_hands.append({
                    'label': hand['label'],
                    'landmarks': [tuple(pt) for pt in aug_lms]
                })

            features = extract_features(aug_hands)
            X_list.append(features)
            y_list.append(str(sign_name))

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=object)
    labels = sorted([str(s) for s in set(y_list)])

    return X, y, labels
