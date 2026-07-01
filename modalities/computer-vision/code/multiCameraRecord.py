# multi_cam_record_headless.py
import os, threading, signal, sys, time
from datetime import datetime
import pyzed.sl as sl

# ---------------------------------------------------------------------------
# Camera labelling
# ---------------------------------------------------------------------------
# Map each physical camera's serial number to a stable label ("cam1"/"cam2").
# This keeps "camera 1" and "camera 2" pinned to the same physical device
# across runs, regardless of the (unstable) order get_device_list() returns.
#
# TODO: replace the placeholder serial numbers below with your real ones.
#       You can find them printed at startup (this script logs every detected
#       serial) or via the ZED_Explorer tool.
CAMERA_LABELS = {
    # <serial_number>: "<label>",
    111111111: "cam1",
    222222222: "cam2",
}

def label_for(serial):
    """Return the stable label for a serial, or a safe serial-based fallback."""
    # Fallback keeps recordings uniquely named even if the serial isn't mapped
    # yet, so nothing is ever overwritten while CAMERA_LABELS is unfilled.
    return CAMERA_LABELS.get(serial, f"cam-SN{serial}")

STOP = False
def on_sigint(sig, frame):
    global STOP; STOP = True
signal.signal(signal.SIGINT, on_sigint)

def record_one(serial, out_dir, session_stamp, fps=30):
    init = sl.InitParameters()
    init.set_from_serial_number(serial)
    init.camera_resolution = sl.RESOLUTION.AUTO
    init.camera_fps = fps
    init.depth_mode = sl.DEPTH_MODE.NONE  # pure recording needs no depth; set NEURAL/PERFORMANCE if you add depth later

    cam = sl.Camera()
    if cam.open(init) != sl.ERROR_CODE.SUCCESS:
        print(f"[{serial}] open failed"); return

    os.makedirs(out_dir, exist_ok=True)
    # Filename: <label>_<date>_<time>.svo2  e.g. cam1_2026-07-01_14-32-05.svo2
    # - label ("cam1"/"cam2") separates the cameras
    # - the shared session date+time stamp prevents overwriting prior videos
    #   and lets you pair cam1/cam2 from the same run (identical stamp)
    label = label_for(serial)
    fname = f"{label}_{session_stamp}.svo2"
    out_path = os.path.join(out_dir, fname)
    rec = sl.RecordingParameters(out_path, sl.SVO_COMPRESSION_MODE.H265)
    if cam.enable_recording(rec) != sl.ERROR_CODE.SUCCESS:
        print(f"[{serial}] enable_recording failed"); cam.close(); return
    print(f"[{serial}] ({label}) recording to {out_path}")

    rt = sl.RuntimeParameters()
    try:
        while not STOP:
            # The Python SDK only writes a frame when grab() returns SUCCESS.
            # Check the return code so failures are logged instead of silently
            # spinning the CPU as fast as possible.
            err = cam.grab(rt)
            if err != sl.ERROR_CODE.SUCCESS:
                print(f"[{serial}] ({label}) grab failed: {err}")
                time.sleep(0.005)  # brief backoff to avoid a busy-spin on repeated failures
    finally:
        cam.disable_recording(); cam.close()
        print(f"[{serial}] ({label}) stopped")

def main():
    devs = sl.Camera.get_device_list()
    if not devs:
        print("No ZED devices found."); return 1

    # Output location, stated explicitly and logged so it's easy to find.
    out_dir = os.path.expanduser("~/zed_rec")
    os.makedirs(out_dir, exist_ok=True)
    print(f"Saving recordings to: {out_dir}")

    # One timestamp for the whole session so cam1/cam2 files line up.
    session_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    threads=[]
    for d in devs:
        print(f"Detected camera serial {d.serial_number} -> {label_for(d.serial_number)}")
        t = threading.Thread(target=record_one, args=(d.serial_number, out_dir, session_stamp))
        t.start(); threads.append(t)

    print("Recording... Ctrl+C to stop")
    for t in threads: t.join()
    return 0

if __name__ == "__main__":
    sys.exit(main())