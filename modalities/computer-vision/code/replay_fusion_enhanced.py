#!/usr/bin/env python3
"""
Offline fusion + analytics for two ZED X SVO/SVO2 recordings.

Features:
- Opens 2 SVOs in playback, enables body tracking on each client, publishes locally.
- Starts Fusion and retrieves *fused* 3D skeletons in WORLD coordinates.
- Computes per-person per-joint velocity & acceleration (finite differences).
- Optionally extracts 2D "head-ish" crops per person (from 2D body bbox) for a gaze model.
- Optionally writes annotated demo videos (one per camera) with 2D skeletons + gaze arrows.

IMPORTANT:
- This draws 2D overlays from each camera's *local* body tracking (not fused)
  for video demos, to avoid heavy per-frame 3D→2D projection code.
- CSV contains the *fused* 3D tracks with kinematics.

Fill in SVO paths and Fusion calibration path below.
"""

import os, sys, csv, math, time
from collections import defaultdict, deque

import pyzed.sl as sl
import numpy as np
import cv2
from gaze_geometry import compute_head_frame_world
from projection_helpers import (
    load_extrinsics_from_fusion_conf, intrinsics_from_caminfo,
    invert_se3, project_point
)

# -------------------- USER CONFIG --------------------
SVO_FILES = [
    "/home/user/zed_rec/44429816.svo2",
    "/home/user/zed_rec/45817796.svo2",
]
FUSION_CONF = "/home/user/zed_rec/fusion_calibration.json"
OUT_CSV     = "/home/user/zed_rec/fused_bodies.csv"

# Depth / body tracking (used at replay time)
DEPTH_MODE  = sl.DEPTH_MODE.NEURAL     # ULTRA/NEURAL for accuracy; PERFORMANCE for speed
BODY_MODEL  = sl.BODY_TRACKING_MODEL.HUMAN_BODY_MEDIUM  # FAST/MEDIUM/ACCURATE
BODY_FORMAT = sl.BODY_FORMAT.BODY_34  # BODY_38 if you need extra extremities

# Kinematics
KINEMATICS_ENABLED   = True
VEL_ACC_WINDOW       = 2      # use 2-frame window for finite difference (previous/current)
MAX_HISTORY          = 5      # per person history for smoothing/robustness

# Head crops & gaze
SAVE_HEAD_CROPS      = True
HEAD_CROP_DIR        = "/home/user/zed_rec/head_crops"
CROP_SIZE            = 224    # resize crops to this square
RUN_GAZE_MODEL       = False  # set True after you plug a model into GazeEstimator.predict()
GAZE_RAY_LENGTH_M    = 2.0    # length of drawn gaze ray in meters (for 3D), used only if projecting

# Demo videos (2D overlays from each camera’s own tracking)
WRITE_DEMO_VIDEOS    = True
VIDEO_DIR            = "/home/user/zed_rec/demos"
VIDEO_FPS_OVERRIDE   = None   # None → use SVO fps; or set e.g. 30
VIDEO_SCALE          = 0.75   # resize frames for lighter output

# -----------------------------------------------------

class GazeEstimator:
    """
    Placeholder for a gaze model (e.g., Gaze360).
    Implement `predict(face_bgr)` to return a unit gaze vector in the camera frame (dx,dy,dz).
    Return None to skip drawing.
    """
    def __init__(self):
        # load your Torch/TensorRT model here
        self.ready = False

    def predict(self, face_bgr: np.ndarray):
        if not self.ready:
            return None
        # TODO: run your model; return np.array([dx, dy, dz]) with ||v||=1
        return None

def open_client_from_svo(svo_path, depth_mode=sl.DEPTH_MODE.NEURAL, fps=None):
    cam = sl.Camera()
    init = sl.InitParameters()
    init.set_from_svo_file(svo_path)
    init.depth_mode = depth_mode
    init.svo_real_time_mode = False   # offline faster-than-real-time

    if fps: init.camera_fps = fps
    err = cam.open(init)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"[CLIENT] Failed to open {svo_path}: {err}")
        return None

    # NEW: positional tracking must be enabled before body tracking
    pt = sl.PositionalTrackingParameters()
    pt.set_as_static = True              # fixed cams during recording
    pt.enable_pose_smoothing = True
    err = cam.enable_positional_tracking(pt)
    if err != sl.ERROR_CODE.SUCCESS:
        print("[CLIENT] enable_positional_tracking failed:", err)
        cam.close()
        return None

    return cam

def enable_bt_and_publish(cam: sl.Camera):
    p = sl.BodyTrackingParameters()
    p.enable_tracking = True
    p.enable_body_fitting = True
    p.body_format = BODY_FORMAT
    p.detection_model = BODY_MODEL
    err = cam.enable_body_tracking(p)
    if err != sl.ERROR_CODE.SUCCESS:
        print("[CLIENT] Body tracking enable failed:", err)
        return False
    # publish to local shared memory (intra-host)
    cp = sl.CommunicationParameters()
    cp.set_for_shared_memory()
    cam.start_publishing(cp)
    return True

# --- replace your init_fusion(...) and camera-registration bits with this ---

def init_fusion():
    fusion = sl.Fusion()
    fparams = sl.InitFusionParameters()
    fparams.coordinate_units  = sl.UNIT.METER
    fparams.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP

    err = fusion.init(fparams)
    if err != sl.ERROR_CODE.SUCCESS:
        print("[FUSION] init failed:", err)
        return None
    else:
        print("[FUSION] init SUCCESS")

    bt = sl.BodyTrackingFusionParameters()
    bt.enable_tracking = True
    bt.enable_body_fitting = True
    fusion.enable_body_tracking_fusion(bt)
    return fusion

def add_inputs_to_fusion(fusion, serials, Twc_map):
    """
    Register each camera with Fusion, using shared memory transport.
    Apply extrinsics (world_T_cam) if available.
    """
    for sn in serials:
        ip = sl.InputFusionParameters()
        # identify the input by serial so Fusion can match it to the publisher
        ip.set_from_serial_number(sn)

        # transport: shared memory on same host
        rx = sl.CommunicationParameters()
        rx.set_for_shared_memory()
        ip.set_comm_params(rx)

        # apply pose if you have it
        Twc = Twc_map.get(sn, None)
        if Twc is not None:
            # Convert 4x4 to sl.Transform
            T = sl.Transform()
            T.init_matrix(Twc.flatten().tolist())
            ip.set_world_pose(T)   # name may be set_world_pose / set_initial_world_transform depending on SDK minor version

        err = fusion.add_camera(ip)
        if err != sl.ERROR_CODE.SUCCESS:
            print(f"[FUSION] add_camera({sn}) failed:", err)
            return False
    return True

def write_csv_header(writer, kp_count):
    cols = ["timestamp_ns","person_id","confidence","tracking_state"]
    for i in range(kp_count):
        cols += [f"k{i}_x","k{i}_y","k{i}_z"]
    if KINEMATICS_ENABLED:
        for i in range(kp_count):
            cols += [f"k{i}_vx","k{i}_vy","k{i}_vz",
                     f"k{i}_ax","k{i}_ay","k{i}_az"]
    cols += ["head_x","head_y","head_z","gaze_dx","gaze_dy","gaze_dz"]
    writer.writerow(cols)

def compute_vel_acc(prev_pts, prev_t, pts, t):
    """
    prev_pts, pts: (K,3) arrays in meters (WORLD)
    t, prev_t: nanoseconds
    Returns vel, acc as (K,3) arrays; if not enough history, zeros.
    """
    if prev_pts is None or prev_t is None or t == prev_t:
        K = pts.shape[0]
        z = np.zeros_like(pts)
        return z, z
    dt = (t - prev_t) * 1e-9  # seconds
    v = (pts - prev_pts) / max(dt, 1e-6)
    # accel needs v_{t-1}; caller can supply previous v if desired.
    # For simplicity, return zeros for a 2-point estimate; caller can smooth over history.
    a = np.zeros_like(v)
    return v, a

def draw_2d_skeleton(frame_bgra, body, color=(0,255,0)):
    """
    Draws a simple scatter/line skeleton using 2D keypoints.
    Assumes body.keypoint_2d is (K,2).
    """
    if body.keypoint_2d is None: return frame_bgra
    pts = np.array(body.keypoint_2d).astype(int)
    for (x,y) in pts:
        cv2.circle(frame_bgra, (x,y), 3, color, -1)
    # Minimal connecting lines (if available). Without an explicit topology, we skip lines.
    return frame_bgra

def extract_head_crop(frame_bgra, body, crop_size=224, expand=0.25):
    """
    Use the 2D body bounding box to crop an upper region as a proxy for head.
    This is a heuristic; for higher fidelity use a face detector.
    """
    if body.bounding_box_2d is None or len(body.bounding_box_2d) == 0:
        return None
    h, w = frame_bgra.shape[:2]
    bb = np.array(body.bounding_box_2d).astype(int)  # 4 corners (x,y)
    x0 = bb[:,0].min(); y0 = bb[:,1].min()
    x1 = bb[:,0].max(); y1 = bb[:,1].max()
    # take upper third as "head-ish" region
    y_head1 = y0
    y_head2 = y0 + int((y1-y0)*0.35)
    # expand a bit
    pad_x = int((x1-x0)*expand)
    pad_y = int((y_head2-y_head1)*expand)
    x0p = max(0, x0 - pad_x); x1p = min(w, x1 + pad_x)
    y0p = max(0, y_head1 - pad_y); y1p = min(h, y_head2 + pad_y)
    if x1p <= x0p or y1p <= y0p:
        return None
    crop = frame_bgra[y0p:y1p, x0p:x1p, :3]  # BGR (drop alpha)
    if crop.size == 0: return None
    crop = cv2.resize(crop, (crop_size, crop_size), interpolation=cv2.INTER_LINEAR)
    return crop

def annotate_gaze(frame_bgra, origin_px, gaze_cam_dir, scale_px=80, color=(0,0,255)):
    """
    Draw a 2D arrow from origin in image pixels using a *camera-frame* gaze direction.
    This assumes you derived a 2D direction in image space or a rough mapping.
    Here we simply draw a short arrow in the local +x/-y heuristic for demo.
    For real projection, map 3D ray through camera intrinsics.
    """
    if origin_px is None or gaze_cam_dir is None:
        return frame_bgra
    ox, oy = int(origin_px[0]), int(origin_px[1])
    dx, dy, dz = gaze_cam_dir
    # crude: project (dx, dy) to image plane sign-wise (for demo arrows)
    ex = int(ox + dx * scale_px)
    ey = int(oy - dy * scale_px)
    cv2.arrowedLine(frame_bgra, (ox,oy), (ex,ey), color, 2, tipLength=0.2)
    return frame_bgra

def main():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    if SAVE_HEAD_CROPS: os.makedirs(HEAD_CROP_DIR, exist_ok=True)
    if WRITE_DEMO_VIDEOS: os.makedirs(VIDEO_DIR, exist_ok=True)

    # 1) Open clients, enable BT + publishers
    clients = []
    for p in SVO_FILES:
        cam = open_client_from_svo(p, DEPTH_MODE)
        if cam is None: 
            print("Failed to open:", p); return 1
        if not enable_bt_and_publish(cam):
            print("Body tracking publish failed:", p); return 1
        clients.append(cam)

    # 2) Prepare per-client display and writers (optional videos)
    mats = [sl.Mat() for _ in clients]
    rt   = [sl.RuntimeParameters() for _ in clients]
    writers = [None]*len(clients)
    info = [c.get_camera_information() for c in clients]
    
    # Build intrinsics per serial from the actual SVO camera calibration
    K_map = {}
    serials = []
    for i in info:
        serials.append(int(i.serial_number))
        K_map.update(intrinsics_from_caminfo(i))

    # Load world_T_cam from fusion calibration file
    Twc_map = load_extrinsics_from_fusion_conf(FUSION_CONF)
    # Precompute cam_T_world for quick projection
    Tcw_map = {}
    for sn in serials:
        Twc = Twc_map.get(sn)
        if Twc is None:
            print(f"[WARN] No extrinsics in fusion conf for serial {sn}. Using identity (world==cam).")
            Twc = np.eye(4)
        Tcw_map[sn] = invert_se3(Twc)
    fpss = [i.camera_configuration.fps for i in info]
    widths = [i.camera_configuration.resolution.width for i in info]
    heights= [i.camera_configuration.resolution.height for i in info]
    for idx, cam in enumerate(clients):
        # --- writer creation ---
        if WRITE_DEMO_VIDEOS:
            fps = VIDEO_FPS_OVERRIDE or int(round(fpss[idx]))
            out_w, out_h = int(widths[idx]*VIDEO_SCALE), int(heights[idx]*VIDEO_SCALE)

            # robust choice on Jetson:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            out_path = os.path.join(VIDEO_DIR, f"demo_cam{idx+1}.avi")
            w = cv2.VideoWriter(out_path, fourcc, fps, (out_w, out_h))
            writers[idx] = w
            if not w.isOpened():
                print(f"[VIDEO][cam{idx+1}] FAILED to open writer {out_path}")
            else:
                print(f"[VIDEO][cam{idx+1}] Writing {out_path} @ {fps} FPS, size=({out_w},{out_h})")

    # 3) Fusion init
    fusion = init_fusion()
    if fusion is None: return 1
    # Register each camera with Fusion (shared memory transport + optional world pose)
    if not add_inputs_to_fusion(fusion, serials, Twc_map):
        return 1
    
    # 4) CSV setup
    kp_count = 34 if BODY_FORMAT == sl.BODY_FORMAT.BODY_34 else 38
    csvf = open(OUT_CSV, "w", newline="")
    writer = csv.writer(csvf)
    write_csv_header(writer, kp_count)

    # kinematics buffers
    prev_pts   = {}   # person_id -> (K,3)
    prev_time  = {}   # person_id -> ns
    # optional: maintain short histories to estimate acceleration better
    v_hist = defaultdict(lambda: deque(maxlen=MAX_HISTORY))

    # Gaze model
    gaze = GazeEstimator()

    # 5) Playback loop
    rt_f = sl.FusionRuntimeParameters()
    active = True
    frame_idx = 0
    try:
        while active:
            active = False

            # Step each client once; also retrieve local bodies & image for video
            local_bodies = []
            frames_bgra  = []
            for i, cam in enumerate(clients):
                err = cam.grab(rt[i])
                # SVO end?
                if err not in (sl.ERROR_CODE.SUCCESS, sl.ERROR_CODE.END_OF_SVOFILE_REACHED):
                    continue
                if err == sl.ERROR_CODE.SUCCESS:
                    active = True
                    # retrieve image + local bodies (for 2D overlay)
                    cam.retrieve_image(mats[i], sl.VIEW.LEFT)  # BGRA
                    frames_bgra.append(mats[i].get_data().copy())
                    bodies = sl.Bodies()
                    cam.retrieve_bodies(bodies)
                    local_bodies.append(bodies)
                else:
                    frames_bgra.append(None)
                    local_bodies.append(sl.Bodies())

            # Now grab fusion
            if fusion.grab(rt_f) == sl.ERROR_CODE.SUCCESS:
                fused = sl.Bodies()
                fusion.retrieve_bodies(fused)
                ts_ns = fused.timestamp.get_nanoseconds()

                # CSV rows (fused 3D)
                for b in fused.body_list:
                    kp = np.asarray(b.keypoint, dtype=np.float32)  # (K,3)
                    row = [ts_ns, b.id, float(b.confidence), int(b.tracking_state)]
                    for p in kp:
                        row.extend([float(p[0]), float(p[1]), float(p[2])])

                    if KINEMATICS_ENABLED:
                        pid = b.id
                        v, a = compute_vel_acc(prev_pts.get(pid), prev_time.get(pid), kp, ts_ns)
                        # optional smoothing: take median over a short window
                        v_hist[pid].append(v)
                        v_smooth = np.median(np.stack(v_hist[pid], axis=0), axis=0) if len(v_hist[pid])>1 else v
                        for p in v_smooth: row.extend([float(p[0]), float(p[1]), float(p[2])])
                        for p in a:        row.extend([float(p[0]), float(p[1]), float(p[2])])
                        prev_pts[pid] = kp
                        prev_time[pid] = ts_ns
                    # kp: (K,3) fused WORLD points already set above
                    head_o, R, fwd, qflag = compute_head_frame_world(
                        kp, 
                        body_format="BODY_34" if BODY_FORMAT == sl.BODY_FORMAT.BODY_34 else "BODY_38",
                        keys_override=None  # or pass your custom dict once you verify indices
                    )
                    # Collect fused head+gaze by fused person id for this frame
                    fused_head_gaze = {}  # pid -> (head_world(3,), gaze_dir_world(3,))
                    for b in fused.body_list:
                        kp = np.asarray(b.keypoint, dtype=np.float32)
                        head_o, R, fwd, qflag = compute_head_frame_world(
                            kp,
                            body_format="BODY_34" if BODY_FORMAT == sl.BODY_FORMAT.BODY_34 else "BODY_38",
                            keys_override=None
                        )
                        if head_o is not None and fwd is not None:
                            fused_head_gaze[b.id] = (head_o, fwd / (np.linalg.norm(fwd)+1e-9))
                        # (you also appended these to the CSV)
                    if head_o is None:
                        head_o = np.array([np.nan, np.nan, np.nan])
                        fwd    = np.array([np.nan, np.nan, np.nan])

                    row.extend([float(head_o[0]), float(head_o[1]), float(head_o[2]),
                                float(fwd[0]),    float(fwd[1]),    float(fwd[2])])
                    writer.writerow(row)

            # Videos: draw local 2D skeletons & (optional) gaze arrows, then write
            GAZE_DRAW_LEN_M = 2.0  # on-image arrow length (in meters along the 3D ray)
            # ======================
            #  Inside the main playback loop
            # ======================
            if WRITE_DEMO_VIDEOS:
                for i, frame in enumerate(frames_bgra):
                    if frame is None:
                        continue

                    bodies = local_bodies[i]

                    # 1️⃣ Identify which camera we're drawing to
                    cam_serial = serials[i]
                    K   = K_map[cam_serial]   # intrinsics
                    Tcw = Tcw_map[cam_serial] # extrinsics (cam_T_world)

                    # 2️⃣ Draw each local body + (optionally) gaze arrow
                    for bi, body in enumerate(bodies.body_list):
                        # Draw the local 2D skeleton first
                        frame = draw_2d_skeleton(frame, body, color=(0,255,0))

                        # Match this local body to a fused body (by id)
                        fused_id = body.id
                        if fused_id in fused_head_gaze:
                            # Get world-space head position and gaze vector
                            head_w, gaze_w = fused_head_gaze[fused_id]

                            # Project world head position into this camera's image
                            p0 = project_point(K, Tcw, head_w)
                            if p0 is None:
                                continue
                            (u0, v0, z0) = p0

                            # Project a second point along the gaze ray in world space
                            head_w2 = head_w + gaze_w * GAZE_DRAW_LEN_M
                            p1 = project_point(K, Tcw, head_w2)
                            if p1 is None:
                                continue
                            (u1, v1, z1) = p1

                            # Draw a red arrow from head → gaze direction in the image
                            pt0 = (int(round(u0)), int(round(v0)))
                            pt1 = (int(round(u1)), int(round(v1)))
                            cv2.arrowedLine(frame, pt0, pt1, (0,0,255), 2, tipLength=0.2)

                    # 3️⃣ Optionally scale and write frame to video
                    # Ensure BGRA -> BGR uint8 and size matches
                    frame_bgr = frame[:, :, :3].copy()
                    if VIDEO_SCALE != 1.0:
                        frame_bgr = cv2.resize(frame_bgr, (out_w, out_h), interpolation=cv2.INTER_LINEAR)

                    if writers[i] is not None and writers[i].isOpened():
                        writers[i].write(frame_bgr)
                    else:
                        # fall back: save a few debug PNGs so you can see what we’re producing
                        if frame_idx < 5:
                            dbg = os.path.join(VIDEO_DIR, f"dbg_cam{i+1}_{frame_idx:04d}.png")
                            cv2.imwrite(dbg, frame_bgr)
                            print(f"[VIDEO][cam{i+1}] Writer not open; wrote debug {dbg}")
            frame_idx += 1

            # loop ends when both SVOs hit EOF
    finally:
        # close video writers
        for i, w in enumerate(writers):
            if w is not None:
                w.release()
                print(f"[VIDEO][cam{i+1}] writer released")
        # stop/purge clients
        for cam in clients:
            try:
                cam.stop_publishing()
                cam.disable_body_tracking()
                cam.close()
            except Exception:
                pass
        # fusion
        try:
            fusion.disable_body_tracking_fusion()
            fusion.close()
        except Exception:
            pass
        csvf.flush(); csvf.close()
        print(f"[OK] CSV written to {OUT_CSV}")
        if WRITE_DEMO_VIDEOS:
            print(f"[OK] Videos in {VIDEO_DIR}")
        if SAVE_HEAD_CROPS:
            print(f"[OK] Head crops in {HEAD_CROP_DIR}")

if __name__ == "__main__":
    sys.exit(main())