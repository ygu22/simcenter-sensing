# multi_cam_record_headless.py
import os, shutil, threading, signal, sys, time, json
from datetime import datetime
import pyzed.sl as sl

# ---------------------------------------------------------------------------
# Camera labelling
# ---------------------------------------------------------------------------
# Map each physical camera's serial number to a stable label ("cam1"/"cam2").
# This keeps "camera 1" and "camera 2" pinned to the same physical device
# across runs, regardless of the (unstable) order get_device_list() returns.
#
# The real serial->label map lives in a camera_roles.json deployed next to
# this script (gitignored — full serials stay out of the public repo, see
# docs/identifiers.md rule 4), e.g. {"12345678": "cam1", "87654321": "cam2"}.
# Serials are printed at startup and shown in the ZED_Explorer tool.
CAMERA_LABELS = {
    # <serial_number>: "<label>",  — placeholders; overridden by camera_roles.json
    111111111: "cam1",
    222222222: "cam2",
}

_ROLES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "camera_roles.json")
# Serials listed in camera_roles.json are the cameras this rig is SUPPOSED to
# have. Used below to refuse to record a partial rig (see check_expected_cameras).
EXPECTED_SERIALS = set()
if os.path.exists(_ROLES_PATH):
    with open(_ROLES_PATH) as _f:
        _roles = {int(k): str(v) for k, v in json.load(_f).items()}
    CAMERA_LABELS.update(_roles)
    EXPECTED_SERIALS = set(_roles)
else:
    print(f"WARNING: no camera_roles.json next to this script ({_ROLES_PATH}).")
    print("         Recordings will be named cam-SN<serial>_* instead of cam1_*/cam2_*,")
    print("         and the expected-camera check below is disabled. See code/README.md.")

def label_for(serial):
    """Return the stable label for a serial, or a safe serial-based fallback."""
    # Fallback keeps recordings uniquely named even if the serial isn't mapped
    # yet, so nothing is ever overwritten while CAMERA_LABELS is unfilled.
    return CAMERA_LABELS.get(serial, f"cam-SN{serial}")

STOP = False
def on_stop_signal(sig, frame):
    global STOP; STOP = True
# SIGINT is the normal Ctrl+C stop. SIGTERM matters just as much: if the
# process is killed without running the shutdown path, disable_recording() is
# never called and the SVO is left unfinalized -- which the SDK later reports
# as "Corruption detected in SVO file" and AUTO-REPAIRS BY TRUNCATING IT.
# That is one plausible route to the ~80% data loss on 2026-07-23, so make an
# ordinary terminate stop the recording cleanly instead.
signal.signal(signal.SIGINT, on_stop_signal)
try:
    signal.signal(signal.SIGTERM, on_stop_signal)
except (AttributeError, ValueError, OSError):
    pass  # SIGTERM unavailable on this platform

# Measured on real two-camera sessions (2026-06-17, 2026-07-23): ~4 MB/s per
# camera of H.265 SVO2. Used to turn free disk into "minutes of headroom".
MB_PER_S_PER_CAMERA = 4.0
ABORT_BELOW_MINUTES = 5      # refuse to start; a mid-session disk-full is unrecoverable
WARN_BELOW_MINUTES  = 20     # start, but say so loudly

def check_disk_headroom(out_dir, n_cameras):
    """Return True if it is safe to start recording, False to abort."""
    try:
        free_bytes = shutil.disk_usage(out_dir).free
    except OSError as e:
        print(f"WARNING: could not check free space on {out_dir}: {e}")
        return True
    rate = MB_PER_S_PER_CAMERA * max(n_cameras, 1)
    minutes = free_bytes / (1024 * 1024) / rate / 60.0
    print(f"Free space: {free_bytes / (1024**3):.1f} GB "
          f"-> ~{minutes:.0f} min of headroom at {rate:.0f} MB/s ({n_cameras} cameras)")
    if minutes < ABORT_BELOW_MINUTES:
        print(f"ABORT: under {ABORT_BELOW_MINUTES} min of recording headroom. "
              f"Free space before recording — a disk-full mid-session cannot be recovered.")
        return False
    if minutes < WARN_BELOW_MINUTES:
        print(f"WARNING: only ~{minutes:.0f} min of headroom. Confirm this covers the "
              f"planned session before continuing.")
    return True

def check_expected_cameras(detected_serials):
    """Refuse to record a partial rig when camera_roles.json says what to expect.

    Fusion needs every camera, so a session recorded with a camera missing
    CANNOT be fused and is wasted — and without this check it fails silently:
    an unplugged camera simply does not appear in get_device_list(), so the
    script would happily record a useless single-camera session and nobody
    would find out until processing.
    """
    if not EXPECTED_SERIALS:
        return True  # no roles file; nothing to check against
    missing = EXPECTED_SERIALS - set(detected_serials)
    if missing:
        print(f"ABORT: expected cameras {sorted(EXPECTED_SERIALS)} per camera_roles.json, "
              f"but {sorted(missing)} were not detected.")
        print("       Check power/cabling and re-run. Recording without every camera")
        print("       produces data that cannot be fused.")
        return False
    extra = set(detected_serials) - EXPECTED_SERIALS
    if extra:
        print(f"WARNING: unexpected camera(s) {sorted(extra)} detected and will also "
              f"record (not in camera_roles.json).")
    return True

# Fusion needs every camera's data, so one camera dying mid-session makes the
# rest of the recording useless on its own. ~3s of consecutive grab failures
# (rather than a single blip) trips this, then all cameras stop together
# instead of one camera silently recording alone for the rest of the session.
MAX_CONSECUTIVE_GRAB_FAILURES = 90

def open_camera(serial, fps=30):
    # Opening a ZED camera is NOT safe to race across threads — the first
    # open() in a process does GPU/CUDA context init, and opening multiple
    # cameras concurrently from separate threads can make every open() fail
    # at once ("Camera::open() has not been called" style errors on all
    # cameras). Cameras must be opened one at a time in a single thread;
    # only the grab loop afterward is safe to parallelize.
    init = sl.InitParameters()
    init.set_from_serial_number(serial)
    init.camera_resolution = sl.RESOLUTION.AUTO
    init.camera_fps = fps
    init.depth_mode = sl.DEPTH_MODE.NONE  # pure recording needs no depth; set NEURAL/PERFORMANCE if you add depth later

    cam = sl.Camera()
    err = cam.open(init)
    return cam, err

def record_one(cam, serial, label, out_dir, session_stamp):
    global STOP
    # Filename: <label>_<date>_<time>.svo2  e.g. cam1_2026-07-01_14-32-05.svo2
    # - label ("cam1"/"cam2") separates the cameras
    # - the shared session date+time stamp prevents overwriting prior videos
    #   and lets you pair cam1/cam2 from the same run (identical stamp)
    fname = f"{label}_{session_stamp}.svo2"
    out_path = os.path.join(out_dir, fname)
    rec = sl.RecordingParameters(out_path, sl.SVO_COMPRESSION_MODE.H265)
    if cam.enable_recording(rec) != sl.ERROR_CODE.SUCCESS:
        print(f"[{serial}] ({label}) enable_recording failed"); cam.close()
        STOP = True  # this camera never started; the rest of the rig alone isn't useful for fusion
        return
    print(f"[{serial}] ({label}) recording to {out_path}")

    rt = sl.RuntimeParameters()
    consecutive_failures = 0
    try:
        while not STOP:
            # The Python SDK only writes a frame when grab() returns SUCCESS.
            # Check the return code so failures are logged instead of silently
            # spinning the CPU as fast as possible.
            err = cam.grab(rt)
            if err != sl.ERROR_CODE.SUCCESS:
                consecutive_failures += 1
                print(f"[{serial}] ({label}) grab failed: {err} ({consecutive_failures} in a row)")
                if consecutive_failures >= MAX_CONSECUTIVE_GRAB_FAILURES:
                    print(f"[{serial}] ({label}) too many consecutive grab failures — stopping all cameras.")
                    STOP = True
                    break
                time.sleep(0.005)  # brief backoff to avoid a busy-spin on repeated failures
            else:
                consecutive_failures = 0
    finally:
        cam.disable_recording(); cam.close()
        print(f"[{serial}] ({label}) stopped")

def main():
    devs = sl.Camera.get_device_list()
    if not devs:
        print("No ZED devices found."); return 1

    # Fail BEFORE the subject is in the room, not after a wasted session.
    if not check_expected_cameras([d.serial_number for d in devs]):
        return 1

    # Output location, stated explicitly and logged so it's easy to find.
    out_dir = os.path.expanduser("~/zed_rec")
    os.makedirs(out_dir, exist_ok=True)
    print(f"Saving recordings to: {out_dir}")

    if not check_disk_headroom(out_dir, len(devs)):
        return 1

    # One timestamp for the whole session so cam1/cam2 files line up.
    session_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Open every camera sequentially, in this thread, before starting any
    # grab loops — see the note in open_camera() for why this can't be
    # parallelized.
    opened = []
    for d in devs:
        serial = d.serial_number
        label = label_for(serial)
        print(f"Detected camera serial {serial} -> {label}")
        cam, err = open_camera(serial)
        if err != sl.ERROR_CODE.SUCCESS:
            print(f"[{serial}] ({label}) open failed: {err}")
            try:
                cam.close()   # release the handle so a retry can succeed
            except Exception:
                pass
            continue
        opened.append((cam, serial, label))

    if not opened:
        print("No cameras opened successfully."); return 1
    # A partial rig cannot be fused, so this is a failed session, not a
    # degraded one. Stop now rather than recording something unusable —
    # and close what we did open so a retry starts clean.
    if len(opened) < len(devs):
        print(f"ABORT: only {len(opened)}/{len(devs)} detected cameras opened. "
              f"Recording without every camera produces data that cannot be fused.")
        for cam, serial, label in opened:
            try:
                cam.close()
            except Exception:
                pass
        return 1

    threads=[]
    for cam, serial, label in opened:
        t = threading.Thread(target=record_one, args=(cam, serial, label, out_dir, session_stamp))
        t.start(); threads.append(t)

    print("Recording... Ctrl+C to stop")
    for t in threads: t.join()
    return 0

if __name__ == "__main__":
    sys.exit(main())