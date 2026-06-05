# gaze_geometry.py
import numpy as np

# ---- Keypoint index maps (adjust if needed for your ZED BODY format) ----
# These defaults work for many ZED BODY_34/38 builds, but verify once.
# Provide None for missing points; code will fallback.
KEYS_BODY34 = dict(
    neck=2, head_top=4, nose=26, left_eye=27, right_eye=28,
    left_shoulder=5, right_shoulder=6
)
KEYS_BODY38 = dict(
    neck=2, head_top=4, nose=34, left_eye=35, right_eye=36,
    left_shoulder=7, right_shoulder=8
)

def _safe_get(pt_list, idx):
    if idx is None: return None
    if idx < 0 or idx >= len(pt_list): return None
    p = pt_list[idx]
    if p is None: return None
    # Some SDKs return [nan,nan,nan] for missing joints
    if any([not np.isfinite(v) for v in p]): return None
    return np.array(p, dtype=float)

def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v

def _orthonormal_basis(forward, right_hint):
    f = _unit(forward)
    r = right_hint - np.dot(right_hint, f) * f  # remove forward component
    r = _unit(r) if np.linalg.norm(r) > 1e-9 else np.array([1.0,0.0,0.0])
    u = np.cross(r, f)
    u = _unit(u) if np.linalg.norm(u) > 1e-9 else np.array([0.0,1.0,0.0])
    # Re-orthogonalize right from u × f to ensure right-handed frame
    r = np.cross(u, f)
    return r, u, f

def compute_head_frame_world(
    keypoints_world, body_format="BODY_34",
    keys_override=None
):
    """
    Args:
      keypoints_world: list/array of shape (K,3) in WORLD coords (meters)
      body_format: "BODY_34" or "BODY_38"
      keys_override: optional dict to override indices (neck, head_top, nose, left_eye, right_eye, left_shoulder, right_shoulder)

    Returns:
      origin (3,), R (3x3), forward (3,), quality_flag (str)
      where forward = R[:, 2]
    """
    kp = keypoints_world
    KEYS = dict(KEYS_BODY34 if body_format=="BODY_34" else KEYS_BODY38)
    if keys_override:
        KEYS.update(keys_override)

    neck   = _safe_get(kp, KEYS.get("neck"))
    head_t = _safe_get(kp, KEYS.get("head_top"))
    nose   = _safe_get(kp, KEYS.get("nose"))
    leye   = _safe_get(kp, KEYS.get("left_eye"))
    reye   = _safe_get(kp, KEYS.get("right_eye"))
    lsh    = _safe_get(kp, KEYS.get("left_shoulder"))
    rsh    = _safe_get(kp, KEYS.get("right_shoulder"))

    # 1) Head center
    quality = "ok"
    if leye is not None and reye is not None:
        head_center = 0.5*(leye + reye)
    elif head_t is not None and neck is not None:
        head_center = 0.5*(head_t + neck)
        quality = "fallback_headtop"
    elif head_t is not None:
        head_center = head_t
        quality = "fallback_headtop_only"
    elif neck is not None:
        head_center = neck
        quality = "fallback_neck_only"
    else:
        return None, None, None, "no_head_points"

    # 2) Forward direction
    if nose is not None:
        forward = nose - head_center
    elif head_t is not None and neck is not None:
        forward = head_t - neck  # up-ish ~ forward fallback
        quality = "fallback_forward_up"
    else:
        forward = np.array([0,0,1.0])  # arbitrary forward
        quality = "fallback_forward_default"

    # 3) Right hint
    if leye is not None and reye is not None:
        right_hint = reye - leye
    elif lsh is not None and rsh is not None:
        right_hint = rsh - lsh
        quality = "fallback_right_shoulder"
    else:
        right_hint = np.array([1.0,0,0])  # default world X

    # 4) Orthonormal frame
    r,u,f = _orthonormal_basis(forward, right_hint)
    R = np.stack([r,u,f], axis=1)  # columns are basis vectors
    return head_center, R, f, quality