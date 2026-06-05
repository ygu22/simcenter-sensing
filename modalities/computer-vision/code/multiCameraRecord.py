# multi_cam_record_headless.py
import os, threading, signal, sys, time
import pyzed.sl as sl

STOP = False
def on_sigint(sig, frame):
    global STOP; STOP = True
signal.signal(signal.SIGINT, on_sigint)

def record_one(serial, out_dir, fps=30):
    init = sl.InitParameters()
    init.set_from_serial_number(serial)
    init.camera_resolution = sl.RESOLUTION.AUTO
    init.camera_fps = fps
    init.depth_mode = sl.DEPTH_MODE.NEURAL  # switch to PERFORMANCE if you want depth later

    cam = sl.Camera()
    if cam.open(init) != sl.ERROR_CODE.SUCCESS:
        print(f"[{serial}] open failed"); return

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{serial}.svo2")
    rec = sl.RecordingParameters(out_path, sl.SVO_COMPRESSION_MODE.H265)
    if cam.enable_recording(rec) != sl.ERROR_CODE.SUCCESS:
        print(f"[{serial}] enable_recording failed"); cam.close(); return
    print(f"[{serial}] recording to {out_path}")

    rt = sl.RuntimeParameters()
    try:
        while not STOP:
            cam.grab(rt)  # <-- Python SDK writes frames on each successful grab
            # (no GUI work here)
    finally:
        cam.disable_recording(); cam.close()
        print(f"[{serial}] stopped")

def main():
    devs = sl.Camera.get_device_list()
    if not devs:
        print("No ZED devices found."); return 1
    out_dir = os.path.expanduser("~/zed_rec")

    threads=[]
    for d in devs:
        t = threading.Thread(target=record_one, args=(d.serial_number, out_dir))
        t.start(); threads.append(t)

    print("Recording... Ctrl+C to stop")
    for t in threads: t.join()
    return 0

if __name__ == "__main__":
    sys.exit(main())