"""
ISL Feature Extractor
Extracts dual-representation 352-dimensional hybrid features from MediaPipe Hand landmarks:
1. Canonical Orthonormal Representation (102 features): 100% rotation-invariant finger pose,
   joint flexion cosine angles, and fingertip pairwise geometry.
2. World Geometric Representation (66 features): Normalized spatial elevation, camera coordinates,
   and wrist positioning to distinguish gestures performed at different body heights (face vs chest vs head).
3. Inter-Hand Interaction Representation (16 features): Dual-hand relative distances, cross-touch,
   and spatial orientation alignment.
Total: 168 (Left Hand) + 168 (Right Hand) + 16 (Inter-Hand) = 352 features.
"""

import numpy as np
import math


def distance_3d(p1, p2):
    """Calculates Euclidean distance between two 3D points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)


def compute_cosine_angle(v1, v2):
    """Computes the cosine of the angle between two 3D vectors."""
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-5 or n2 < 1e-5:
        return 0.0
    cos_val = np.dot(v1, v2) / (n1 * n2)
    return float(np.clip(cos_val, -1.0, 1.0))


def get_finger_states(landmarks):
    """
    Determines whether each of the 5 fingers is extended (1.0) or curled (0.0).
    Landmarks is a list of 21 (x, y, z) tuples.
    """
    if landmarks is None or len(landmarks) < 21:
        return [0.0] * 5

    wrist = landmarks[0]
    states = []

    # 1. Thumb: compare distance from tip (4) to pinky MCP (17) vs IP (3) to pinky MCP (17)
    thumb_tip_dist = distance_3d(landmarks[4], landmarks[17])
    thumb_ip_dist = distance_3d(landmarks[3], landmarks[17])
    states.append(1.0 if thumb_tip_dist > thumb_ip_dist else 0.0)

    # 2. Index finger: tip (8) distance to wrist vs PIP (6) distance to wrist
    states.append(1.0 if distance_3d(landmarks[8], wrist) > distance_3d(landmarks[6], wrist) else 0.0)

    # 3. Middle finger: tip (12) distance to wrist vs PIP (10) distance to wrist
    states.append(1.0 if distance_3d(landmarks[12], wrist) > distance_3d(landmarks[10], wrist) else 0.0)

    # 4. Ring finger: tip (16) distance to wrist vs PIP (14) distance to wrist
    states.append(1.0 if distance_3d(landmarks[16], wrist) > distance_3d(landmarks[14], wrist) else 0.0)

    # 5. Pinky finger: tip (20) distance to wrist vs PIP (18) distance to wrist
    states.append(1.0 if distance_3d(landmarks[20], wrist) > distance_3d(landmarks[18], wrist) else 0.0)

    return states


def normalize_hand_landmarks(landmarks):
    """
    Extracts 168 features for a single hand:
    - 102 Canonical Orthonormal Local Features (rotation-invariant).
    - 63 World Centered & Scaled Coordinates.
    - 3 World Wrist Coordinates.
    Returns np.ndarray of shape (168,).
    """
    if landmarks is None or len(landmarks) < 21:
        return np.zeros(168, dtype=np.float32)

    pts = np.array(landmarks, dtype=np.float32) # shape (21, 3)
    wrist = pts[0]
    centered = pts - wrist

    # 1. Hand scale: distance between wrist (0) and middle MCP (9)
    v_y = centered[9]
    scale = np.linalg.norm(v_y)
    if scale < 1e-4:
        scale = 1.0
    u_y = v_y / scale

    # 2. Palm normal Z-axis using cross product of Index MCP (5) and Pinky MCP (17)
    v_idx = centered[5]
    v_pinky = centered[17]
    u_z = np.cross(v_idx, v_pinky)
    norm_z = np.linalg.norm(u_z)
    if norm_z < 1e-4:
        u_z = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    else:
        u_z = u_z / norm_z

    # 3. Orthogonal X-axis
    u_x = np.cross(u_y, u_z)
    norm_x = np.linalg.norm(u_x)
    if norm_x < 1e-4:
        u_x = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    else:
        u_x = u_x / norm_x

    # Re-orthogonalize Z-axis
    u_z = np.cross(u_x, u_y)

    # Rotation matrix to canonical hand frame (shape 3, 3)
    R = np.vstack([u_x, u_y, u_z])

    # Canonical 3D coordinates (21 * 3 = 63 features, rotation-invariant!)
    canonical_pts = (centered / scale) @ R.T
    coords_63 = canonical_pts.flatten().astype(np.float32)

    # 4. Joint flexion cosine angles (10 features: 2 angles per finger)
    joint_chains = [
        (1, 2, 3, 4),
        (5, 6, 7, 8),
        (9, 10, 11, 12),
        (13, 14, 15, 16),
        (17, 18, 19, 20)
    ]
    angles = []
    for m, p1, p2, tip in joint_chains:
        v1 = pts[p1] - pts[m]
        v2 = pts[p2] - pts[p1]
        v3 = pts[tip] - pts[p2]
        angles.append(compute_cosine_angle(v1, v2))
        angles.append(compute_cosine_angle(v2, v3))
    angles_10 = np.array(angles, dtype=np.float32)

    # 5. Fingertip-to-palm center distances (5 features)
    palm_center = pts[9]
    tip_indices = [4, 8, 12, 16, 20]
    tip_to_palm_5 = np.array([np.linalg.norm(pts[t] - palm_center) / scale for t in tip_indices], dtype=np.float32)

    # 6. Fingertip-to-wrist distances (5 features)
    tip_to_wrist_5 = np.array([np.linalg.norm(pts[t] - wrist) / scale for t in tip_indices], dtype=np.float32)

    # 7. Fingertip-to-fingertip pairwise relative distances (8 features)
    pw = [
        np.linalg.norm(pts[4] - pts[8]) / scale,
        np.linalg.norm(pts[8] - pts[12]) / scale,
        np.linalg.norm(pts[12] - pts[16]) / scale,
        np.linalg.norm(pts[16] - pts[20]) / scale,
        np.linalg.norm(pts[4] - pts[12]) / scale,
        np.linalg.norm(pts[4] - pts[16]) / scale,
        np.linalg.norm(pts[4] - pts[20]) / scale,
        np.linalg.norm(pts[8] - pts[20]) / scale,
    ]
    tip_pw_8 = np.array(pw, dtype=np.float32)

    # 8. Binary finger extension states (5 features)
    finger_states_5 = np.array(get_finger_states(landmarks), dtype=np.float32)

    # 9. Hand orientation in camera coordinates (6 features: u_y and u_z)
    orient_6 = np.concatenate([u_y, u_z]).astype(np.float32)

    # Canonical 102 features
    canon_102 = np.concatenate([
        coords_63,
        angles_10,
        tip_to_palm_5,
        tip_to_wrist_5,
        tip_pw_8,
        finger_states_5,
        orient_6
    ])

    # 10. World Spatial Features (66 features: 63 world centered + 3 wrist coords)
    world_coords_63 = (centered / scale).flatten().astype(np.float32)
    wrist_coords_3 = wrist.astype(np.float32)

    return np.concatenate([canon_102, world_coords_63, wrist_coords_3]).astype(np.float32)


def extract_features(hands_data):
    """
    Extracts fixed-length 352-dimensional hybrid feature vector from detected hands:
    - Left hand features (168)
    - Right hand features (168)
    - Dual-hand presence & inter-hand spatial interaction features (16)
    Total = 352 features.
    """
    left_hand = None
    right_hand = None

    if hands_data:
        for hand in hands_data:
            lbl = hand.get('label', '')
            lms = hand.get('landmarks', [])
            if lbl == 'Left' and left_hand is None:
                left_hand = lms
            elif lbl == 'Right' and right_hand is None:
                right_hand = lms

        # Fallback if labels were ambiguous
        if left_hand is None and right_hand is None and len(hands_data) > 0:
            right_hand = hands_data[0].get('landmarks', [])

    has_left = 1.0 if left_hand is not None else 0.0
    has_right = 1.0 if right_hand is not None else 0.0

    feat_left = normalize_hand_landmarks(left_hand)   # 168
    feat_right = normalize_hand_landmarks(right_hand) # 168

    # Dual-hand inter-relational features (16 features)
    inter_features = np.zeros(16, dtype=np.float32)
    inter_features[0] = has_left
    inter_features[1] = has_right

    if has_left and has_right:
        lwrist = np.array(left_hand[0], dtype=np.float32)
        rwrist = np.array(right_hand[0], dtype=np.float32)

        wrist_disp = rwrist - lwrist
        wrist_dist = float(np.linalg.norm(wrist_disp))

        inter_features[2] = wrist_dist
        inter_features[3] = float(wrist_disp[0])
        inter_features[4] = float(wrist_disp[1])
        inter_features[5] = float(wrist_disp[2])

        # Index tips
        l_idx_tip = np.array(left_hand[8], dtype=np.float32)
        r_idx_tip = np.array(right_hand[8], dtype=np.float32)
        inter_features[6] = float(np.linalg.norm(r_idx_tip - l_idx_tip))

        # Thumb tips
        l_th_tip = np.array(left_hand[4], dtype=np.float32)
        r_th_tip = np.array(right_hand[4], dtype=np.float32)
        inter_features[7] = float(np.linalg.norm(r_th_tip - l_th_tip))

        # Cross thumb-index
        inter_features[8] = float(np.linalg.norm(r_th_tip - l_idx_tip))
        inter_features[9] = float(np.linalg.norm(l_th_tip - r_idx_tip))

        # Middle tips
        l_mid_tip = np.array(left_hand[12], dtype=np.float32)
        r_mid_tip = np.array(right_hand[12], dtype=np.float32)
        inter_features[10] = float(np.linalg.norm(r_mid_tip - l_mid_tip))

        # Palm centers
        l_center = np.array(left_hand[9], dtype=np.float32)
        r_center = np.array(right_hand[9], dtype=np.float32)
        inter_features[11] = float(np.linalg.norm(r_center - l_center))

        # Cross touch
        inter_features[12] = float(np.linalg.norm(r_center - l_idx_tip))
        inter_features[13] = float(np.linalg.norm(l_center - r_idx_tip))

        # Orientation alignment (from indices 96..102 in features)
        uy_l = feat_left[96:99]
        uz_l = feat_left[99:102]
        uy_r = feat_right[96:99]
        uz_r = feat_right[99:102]
        inter_features[14] = float(np.dot(uy_l, uy_r))
        inter_features[15] = float(np.dot(uz_l, uz_r))

    total_vector = np.concatenate([feat_left, feat_right, inter_features])
    return total_vector.astype(np.float32)
