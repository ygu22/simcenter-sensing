#!/usr/bin/env python3
"""
Run replay_fusion_enhanced.py's fusion + arm-angle processing over every
cam1/cam2 SVO2 pair found in a recordings directory, instead of hand-editing
the USER CONFIG block once per session.

multiCameraRecord.py names files <label>_<session_stamp>.svo2, e.g.
cam1_2026-07-01_14-32-05.svo2 / cam2_2026-07-01_14-32-05.svo2 — files that
share a stamp are one session. Each session gets its own subfolder under
--out-dir (named by its stamp) containing fused_bodies.csv and, if enabled
in replay_fusion_enhanced.py, head_crops/ and demos/.

Usage:
    python batch_process_sessions.py \\
        --recordings-dir ~/zed_rec \\
        --fusion-conf ~/zed_rec/fusion_calibration.json \\
        --out-dir ~/cpr_dataset
"""
import argparse, csv, datetime, hashlib, json, os, re, sys, traceback
from collections import Counter, defaultdict

import replay_fusion_enhanced as rfe
from replay_fusion_enhanced import process_session, SAVE_HEAD_CROPS, WRITE_DEMO_VIDEOS

FNAME_RE = re.compile(r"^(?P<label>[^_]+)_(?P<stamp>.+)\.svo2$")

def find_sessions(recordings_dir):
    sessions = defaultdict(dict)  # stamp -> {label: path}
    for fname in os.listdir(recordings_dir):
        m = FNAME_RE.match(fname)
        if not m:
            continue
        sessions[m.group("stamp")][m.group("label")] = os.path.join(recordings_dir, fname)
    return sessions

def _sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(chunk), b""):
            h.update(blk)
    return h.hexdigest()

def write_session_meta(session_out, stamp, svo_files, fusion_conf):
    """Record exactly what produced this session's output.

    A dataset built over weeks will span camera recalibrations and possibly
    config changes. Without provenance there is no way to tell afterwards which
    calibration or coordinate convention a given CSV was built with -- and a
    wrong frame silently corrupts every angle (see changes.txt, 2026-07-27).
    The calibration is hashed so a swapped-but-same-named file is detectable.
    """
    meta = {
        "session_stamp": stamp,
        "processed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "svo_files": [os.path.abspath(p) for p in svo_files],
        "fusion_conf": os.path.abspath(fusion_conf),
        "fusion_conf_sha256": _sha256(fusion_conf),
        "coord_system": str(rfe.COORD_SYSTEM),
        "depth_mode": str(rfe.DEPTH_MODE),
        "body_model": str(rfe.BODY_MODEL),
        "body_format": str(rfe.BODY_FORMAT),
        "arm_angles_enabled": bool(rfe.ARM_ANGLES_ENABLED),
        "sdk_version": str(rfe.sl.Camera.get_sdk_version()),
    }
    try:
        with open(os.path.join(session_out, "session_meta.json"), "w") as f:
            json.dump(meta, f, indent=2)
    except OSError as e:
        print(f"  [warn] could not write session_meta.json: {e}")
    return meta

def qa_session(out_csv, expect_people):
    """Read back the CSV and check the dataset-level QA gates.

    Returns (n_persons, main_coverage_pct, problems[list[str]]).
    """
    problems = []
    try:
        with open(out_csv, newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError as e:
        return 0, 0.0, [f"unreadable CSV: {e}"]
    if not rows:
        return 0, 0.0, ["CSV has no rows"]

    counts = Counter(int(float(r["person_id"])) for r in rows)
    n_persons = len(counts)
    main_pid, main_n = counts.most_common(1)[0]
    frames = len(set(r["timestamp_ns"] for r in rows))
    coverage = 100.0 * main_n / frames if frames else 0.0

    if n_persons != expect_people:
        problems.append(f"{n_persons} person_id(s), expected {expect_people}")
    # Anatomically implausible limb length => phantom track, not a person.
    for pid in counts:
        lens = []
        for r in rows:
            if int(float(r["person_id"])) != pid:
                continue
            try:
                lens.append(float(r["R_upperarm_len_m"]))
            except (KeyError, ValueError):
                pass
        if lens:
            med = sorted(lens)[len(lens) // 2]
            if not (0.20 <= med <= 0.45):
                problems.append(f"person {pid} upper arm {med*1000:.0f} mm (phantom?)")
    return n_persons, coverage, problems

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recordings-dir", required=True, help="Directory of cam1_*/cam2_*.svo2 files, e.g. ~/zed_rec")
    ap.add_argument("--fusion-conf", required=True, help="fusion_calibration.json shared across sessions")
    ap.add_argument("--out-dir", required=True, help="Dataset root; one subfolder per session is created here")
    ap.add_argument("--force", action="store_true", help="Reprocess a session even if its fused_bodies.csv already exists")
    ap.add_argument("--expect-people", type=int, default=1,
                    help="People expected in frame per session (default 1); sessions differing are flagged")
    args = ap.parse_args()

    recordings_dir = os.path.expanduser(args.recordings_dir)
    out_root = os.path.expanduser(args.out_dir)
    fusion_conf = os.path.expanduser(args.fusion_conf)

    sessions = find_sessions(recordings_dir)
    if not sessions:
        print(f"No SVO2 files found in {recordings_dir}")
        return 1

    ok = skipped = failed = 0
    flagged = []   # (stamp, [problems]) for the end-of-run QA summary
    for stamp, files in sorted(sessions.items()):
        if len(files) < 2:
            print(f"[{stamp}] SKIP — only found {sorted(files)}, need both cameras present")
            skipped += 1
            continue

        session_out = os.path.join(out_root, stamp)
        out_csv = os.path.join(session_out, "fused_bodies.csv")
        if os.path.exists(out_csv) and not args.force:
            print(f"[{stamp}] SKIP — {out_csv} already exists (use --force to reprocess)")
            skipped += 1
            continue

        svo_files = [files[label] for label in sorted(files)]  # cam1 before cam2
        head_crop_dir = os.path.join(session_out, "head_crops") if SAVE_HEAD_CROPS else None
        video_dir = os.path.join(session_out, "demos") if WRITE_DEMO_VIDEOS else None

        print(f"[{stamp}] Processing {svo_files} -> {out_csv}")
        try:
            rc = process_session(svo_files, fusion_conf, out_csv,
                                  head_crop_dir=head_crop_dir, video_dir=video_dir)
        except Exception:
            traceback.print_exc()
            rc = 1

        if rc == 0:
            ok += 1
            write_session_meta(session_out, stamp, svo_files, fusion_conf)
            n, cov, problems = qa_session(out_csv, args.expect_people)
            status = "ok" if not problems else "; ".join(problems)
            print(f"[{stamp}] QA: {n} person(s), main track {cov:.0f}% coverage — {status}")
            if problems:
                flagged.append((stamp, problems))
        else:
            print(f"[{stamp}] FAILED (exit {rc})")
            failed += 1

    print(f"\n{ok} processed, {skipped} skipped, {failed} failed — {len(sessions)} sessions found in {recordings_dir}")
    if flagged:
        print(f"\n{len(flagged)} session(s) FLAGGED by QA — review before folding into the dataset:")
        for stamp, problems in flagged:
            print(f"  {stamp}: {'; '.join(problems)}")
        print("A wrong coordinate frame or a phantom track makes every angle in that")
        print("session invalid; see cpr-joint-angles-protocol.md (session acceptance).")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
