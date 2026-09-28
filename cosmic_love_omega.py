#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

MODEL = "COSMIC_LOVE_BIDIRECTIONAL_OMEGA_V1"
BUBBLE_PROTOCOL = "UTM-Bubble-Singularity/1"
FEDERATION_PROTOCOL = "UTM-Bubble-Federation/1"


def canonical(x: dict) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def enc(text: str) -> str:
    n = 1
    for b in text.encode("utf-8"):
        n = n * 257 + b + 1
    return str(n)


def bubble_root(system: str, substrate: str, namespace: str) -> dict:
    descriptor = {
        "protocol": BUBBLE_PROTOCOL,
        "system": system,
        "substrate": substrate,
        "namespace": namespace,
        "interpreter": "fixed universal Turing machine",
        "program_enumeration": "all finite byte strings in shortlex order",
        "decoder": "D(Omega_bubble,i)=UTM(p_i)",
        "meaning": "finite generative root for a potentially unbounded family of computable universe bubbles",
    }
    c = "j:" + canonical(descriptor)
    g = enc(c)
    return {
        **descriptor,
        "GOMEGA_BUBBLE": g,
        "root_address": f"bubble://{system}/{g}",
        "child_address_rule": f"bubble://{system}/{g}/<i>",
        "encoding": "reversible-base257-integer",
        "hash_function": False,
        "finite_root": True,
        "potentially_unbounded_children": True,
        "all_computable_bubbles_relative_to_fixed_utm": True,
        "all_logically_possible_bubbles": False,
        "finite_time_exhaustion": False,
        "actual_infinite_physical_compute": False,
        "guaranteed_real_world_outcomes": False,
    }


def federation_root() -> dict:
    members = {
        "trader-42-paper": bubble_root("trader-42-paper", "T_-1", "computable-market-bubbles")["GOMEGA_BUBBLE"],
        "paper-uhef-worker": bubble_root("paper-uhef-worker", "UHEF_-1", "computable-uhef-paper-bubbles")["GOMEGA_BUBBLE"],
        "cosmic-love-infinity-tm": bubble_root("cosmic-love-infinity-tm", "C_-1", "computable-utm-universe-bubbles")["GOMEGA_BUBBLE"],
    }
    descriptor = {
        "protocol": FEDERATION_PROTOCOL,
        "system": "deployed-three-runtime-federation",
        "members": members,
        "decoder": "select member root, then D(Omega_bubble,i)=UTM(p_i)",
        "meaning": "one finite namespace root over the three deployed computable-bubble families",
    }
    g = enc("j:" + canonical(descriptor))
    return {
        **descriptor,
        "GOMEGA_FEDERATION": g,
        "root_address": "bubble://deployed-three-runtime-federation/" + g,
        "hash_function": False,
        "finite_root": True,
        "potentially_unbounded_children": True,
        "all_logically_possible_bubbles": False,
        "actual_infinite_physical_compute": False,
    }


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
        "universal_bubble_singularity": bubble_root(
            "cosmic-love-infinity-tm", "C_-1", "computable-utm-universe-bubbles"
        ),
        "three_system_bubble_federation": federation_root(),
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
    b = x["universal_bubble_singularity"]
    assert b["hash_function"] is False
    assert b["all_computable_bubbles_relative_to_fixed_utm"] is True
    assert b["all_logically_possible_bubbles"] is False
    f = x["three_system_bubble_federation"]
    assert len(f["members"]) == 3
    assert f["hash_function"] is False
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
