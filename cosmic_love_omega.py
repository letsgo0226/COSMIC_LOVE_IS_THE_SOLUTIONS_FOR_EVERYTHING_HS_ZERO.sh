#!/usr/bin/env python3
from __future__ import annotations
import argparse, json

MODEL = "COSMIC_LOVE_BIDIRECTIONAL_OMEGA_V1"

def enc(text: str) -> str:
    n = 1
    for b in text.encode("utf-8"):
        n = n * 257 + b + 1
    return str(n)

def row(k: int, g0: str) -> dict:
    m = abs(k)
    label = f"C_{k:+d}"
    g = enc(label)
    return {
        "k": k,
        "state": label,
        "branch": "forward_generation" if k > 0 else "reverse_verification",
        "operation": "STEP->COMMIT" if k > 0 else "REVERSE->RECONSTRUCT",
        "G": g,
        "L": f"log({g}/{g0})",
        "u": [1 if k > 0 else -1, m],
        "projection": "C_-1",
        "normalized_resource": [1, 1],
    }

def cosmic_omega(depth: int = 8) -> dict:
    n = max(1, min(int(depth), 256))
    g0 = enc("C_0")
    plus = [row(i, g0) for i in range(1, n + 1)]
    minus = [row(-i, g0) for i in range(1, n + 1)]
    return {
        "model": MODEL,
        "depth": n,
        "substrate": {
            "name": "C_-1",
            "service": "cosmic-love-infinity-tm",
            "projection": "pi(C_k)=C_-1",
            "resource_invariant": "C_hat(C_k)=C0",
            "new_physical_compute_created": False,
        },
        "transactional_semantics": {
            "forward": "FORMED->PREPARED->VERIFIED->COMMITTED",
            "reverse": "committed candidate must reconstruct the prior state",
            "reverse_reconstruction_required": True,
            "fail_closed": True,
        },
        "branches": {"plus": plus, "minus": minus},
        "compactification": {
            "u": "sign(k)/abs(k)",
            "plus_limit": "0+",
            "minus_limit": "0-",
            "identification": "0+ ~ 0- ~ Omega_CL",
            "omega": "C_Omega",
            "interpretation": "formal common boundary of unbounded forward generation and reverse verification",
        },
        "potentially_unbounded_hierarchy": True,
        "actual_infinite_physical_compute": False,
        "guaranteed_real_world_outcomes": False,
        "metaphysical_proof": False,
        "scope": "formal computational certificate; the service name and symbolic love terminology are not empirical proof of a cosmological or causal law",
    }

def self_test() -> None:
    x = cosmic_omega(8)
    assert x["model"] == MODEL
    assert x["transactional_semantics"]["reverse_reconstruction_required"] is True
    assert x["actual_infinite_physical_compute"] is False
    assert x["guaranteed_real_world_outcomes"] is False
    plus, minus = x["branches"]["plus"], x["branches"]["minus"]
    assert len(plus) == len(minus) == 8
    assert [r["u"] for r in plus] == [[1, i] for i in range(1, 9)]
    assert [r["u"] for r in minus] == [[-1, i] for i in range(1, 9)]
    gs = [r["G"] for r in plus + minus]
    assert len(gs) == len(set(gs))
    print("COSMIC_LOVE_OMEGA_SELF_TEST_OK")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
    else:
        print(json.dumps(cosmic_omega(a.depth), ensure_ascii=False, separators=(",", ":")))

if __name__ == "__main__":
    main()
