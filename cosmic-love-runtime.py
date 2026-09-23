from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

KERNEL = Path(os.environ.get("TM_KERNEL", "/app/cosmic-love-infinity-tm.sh"))
STATE = Path(os.environ.get("LOG_TM_STATE", "/data/cosmic-love-state.json"))
JOURNAL = Path(os.environ.get("TM_OPERATION_JOURNAL", "/data/cosmic-love-operations.jsonl"))
META = Path(os.environ.get("TM_META_PATH", "/data/cosmic-love-meta.json"))
POLL_SECONDS = float(os.environ.get("POLL_SECONDS", "2"))
MAX_STEPS = int(os.environ.get("TM_MAX_STEPS", "0"))
FAIL_CLOSED = os.environ.get("TM_FAIL_CLOSED", "1") != "0"

CORE_KEYS = ("t", "pc", "n", "p", "c", "d", "E", "k")
ZERO = {"t": 0, "pc": 0, "n": 0, "p": 1, "c": 2, "d": 2, "E": [0] * 6, "k": 0}


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def digest(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def emit(**event):
    print(canonical({"model": "COSMIC_LOVE_TRANSACTIONAL_TM", **event}), flush=True)


def read_json(path: Path, default):
    if not path.exists():
        return json.loads(canonical(default))
    text = path.read_text().strip()
    return json.loads(text) if text else json.loads(canonical(default))


def core(state):
    merged = {**ZERO, **{k: state[k] for k in state if k in ZERO}}
    merged["E"] = (list(merged.get("E", [])) + [0] * 6)[:6]
    return {k: merged[k] for k in CORE_KEYS}


def invoke_kernel(state_path: Path, command: str):
    env = os.environ.copy()
    env.update(LOG_TM_STATE=str(state_path), CMD=command, N="1")
    result = subprocess.run(
        ["sh", str(KERNEL)],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"kernel {command} failed: {result.stderr.strip()[:240]}")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(f"kernel {command} produced no JSON")
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"kernel {command} emitted invalid JSON") from exc


def append_journal(record):
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    with JOURNAL.open("a") as fh:
        fh.write(canonical(record) + "\n")


def load_meta():
    return read_json(META, {"committed_steps": 0, "last_transition_id": None, "phase": "IDLE"})


def save_meta(meta):
    META.parent.mkdir(parents=True, exist_ok=True)
    tmp = META.with_suffix(META.suffix + ".tmp")
    tmp.write_text(canonical(meta))
    os.replace(tmp, META)


def temp_state(prefix: str):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=prefix, suffix=".json", dir=STATE.parent)
    os.close(fd)
    return Path(name)


def transactional_step():
    if not KERNEL.exists():
        raise RuntimeError(f"kernel missing: {KERNEL}")

    before = core(read_json(STATE, ZERO))
    before_hash = digest(before)
    transition_id = f"cltm-{before['t'] + 1}-{before_hash[:12]}"
    candidate = temp_state("candidate-")
    verifier = temp_state("verify-")

    try:
        candidate.write_text(canonical(before))
        emit(
            phase="FORMED",
            transition_id=transition_id,
            requested_operation="STEP",
            from_t=before["t"],
            from_n=before["n"],
            before_hash=before_hash,
        )

        out = invoke_kernel(candidate, "step")
        after = core(read_json(candidate, ZERO))
        if out.get("C") is not True:
            raise RuntimeError("kernel certificate gate C is false")
        if after["t"] != before["t"] + 1:
            raise RuntimeError("STEP did not advance t by exactly one")
        if after["n"] < before["n"] or after["n"] > before["n"] + 1:
            raise RuntimeError("STEP produced invalid commit-counter delta")

        emit(
            phase="PREPARED",
            transition_id=transition_id,
            requested_operation="STEP",
            candidate_t=after["t"],
            candidate_n=after["n"],
            kernel_C=True,
            kernel_G=out.get("G"),
        )

        shutil.copy2(candidate, verifier)
        reverse_out = invoke_kernel(verifier, "reverse")
        restored = core(read_json(verifier, ZERO))
        reverse_ok = reverse_out.get("CF") is True and restored == before
        if not reverse_ok:
            raise RuntimeError("reverse reconstruction proof failed")

        emit(
            phase="VERIFIED",
            transition_id=transition_id,
            requested_operation="STEP",
            reverse_reconstruction=True,
            restored_hash=digest(restored),
        )

        os.replace(candidate, STATE)
        meta = load_meta()
        meta["committed_steps"] = int(meta.get("committed_steps", 0)) + 1
        meta["last_transition_id"] = transition_id
        meta["phase"] = "COMMITTED"
        meta["godel_operations"] = f"11^{meta['committed_steps']}"
        save_meta(meta)

        record = {
            "phase": "COMMITTED",
            "transition_id": transition_id,
            "operation": "STEP",
            "from_t": before["t"],
            "to_t": after["t"],
            "from_n": before["n"],
            "to_n": after["n"],
            "before_hash": before_hash,
            "after_hash": digest(after),
            "reverse_reconstruction": True,
            "kernel_C": True,
            "kernel_G": out.get("G"),
            "godel_operations": meta["godel_operations"],
        }
        append_journal(record)
        emit(model_state="RUNNING", **record)
        return record

    except Exception as exc:
        aborted = {
            "phase": "ABORTED",
            "transition_id": transition_id,
            "operation": "STEP",
            "from_t": before["t"],
            "before_hash": before_hash,
            "error_type": type(exc).__name__,
            "message": str(exc)[:240],
        }
        append_journal(aborted)
        meta = load_meta()
        meta["phase"] = "ABORTED"
        meta["last_transition_id"] = transition_id
        save_meta(meta)
        emit(model_state="HALTED" if FAIL_CLOSED else "DEGRADED", **aborted)
        if FAIL_CLOSED:
            raise
        return aborted
    finally:
        candidate.unlink(missing_ok=True)
        verifier.unlink(missing_ok=True)


def self_test():
    global STATE, JOURNAL, META, KERNEL
    original = (STATE, JOURNAL, META, KERNEL)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            STATE = root / "state.json"
            JOURNAL = root / "ops.jsonl"
            META = root / "meta.json"
            if not KERNEL.exists():
                raise RuntimeError(f"self-test kernel missing: {KERNEL}")
            a = transactional_step()
            b = transactional_step()
            state = core(read_json(STATE, ZERO))
            meta = load_meta()
            rows = [json.loads(x) for x in JOURNAL.read_text().splitlines() if x.strip()]
            assert a["phase"] == "COMMITTED" and b["phase"] == "COMMITTED"
            assert state["t"] == 2
            assert meta["committed_steps"] == 2
            assert meta["godel_operations"] == "11^2"
            assert len(rows) == 2 and all(r["reverse_reconstruction"] for r in rows)
            print("SELF_TEST_OK")
    finally:
        STATE, JOURNAL, META, KERNEL = original


def main():
    if "--self-test" in sys.argv:
        self_test()
        return

    emit(
        phase="BOOT",
        kernel=str(KERNEL),
        state_path=str(STATE),
        journal_path=str(JOURNAL),
        semantics="FORMED->PREPARED->VERIFIED->COMMITTED",
        fail_closed=FAIL_CLOSED,
    )
    steps = 0
    while True:
        transactional_step()
        steps += 1
        if MAX_STEPS and steps >= MAX_STEPS:
            emit(phase="HALTED", reason="TM_MAX_STEPS reached", committed_steps=steps)
            return
        time.sleep(max(POLL_SECONDS, 0.0))


if __name__ == "__main__":
    main()
