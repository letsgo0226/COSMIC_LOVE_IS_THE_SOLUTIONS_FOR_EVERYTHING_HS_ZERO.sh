#!/usr/bin/env python3
"""UTM-Omega Resident Deployment Protocol v1.0.

This module admits finite, code-backed resident programs into the formal
UTM-Omega direct-limit model. OMEGA_ADMITTED is a logical/formal deployment
state. It is not a claim of actually infinite physical computation and it does
not create GitHub/Railway/host privileges.

Each actually verified stage remains finite.
"""

from __future__ import annotations

from hashlib import sha256
import json
import re
from pathlib import Path
from typing import Any, Dict, Mapping

from synced_utm_layers import omega_verifier

HERE = Path(__file__).resolve().parent
DEFAULT_REGISTRY = HERE / "utm_omega_residents.json"
PROTOCOL = "UTM-Omega-Resident-Deployment/1.0"
STATUS = "OMEGA_ADMITTED"
SHA_RE = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def load_registry(path: Path = DEFAULT_REGISTRY) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resident_valuation(registry: Mapping[str, Any]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for resident in registry.get("residents", []):
        coordinate = int(resident["coordinate"])
        key = str(coordinate)
        if key in out:
            raise ValueError("duplicate resident coordinate")
        out[key] = 1
    return dict(sorted(out.items(), key=lambda kv: int(kv[0])))


def verify_registry(registry: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    r = dict(registry or load_registry())
    residents = r.get("residents", [])
    stage = dict(r.get("stage", {}))
    declared_valuation = {str(k): int(v) for k, v in stage.get("valuation", {}).items()}
    computed_valuation = resident_valuation(r)

    ids = [x.get("id") for x in residents]
    coords = [int(x.get("coordinate", -1)) for x in residents]
    empirical_flags = [x.get("empirical_claim") for x in residents]
    inv = r.get("invariants", {})
    omega_stage = omega_verifier.verify_finite_stage(stage)

    checks = {
        "protocol": r.get("protocol") == "UTM-Omega-Resident-Registry/1.0",
        "world_id": r.get("world_id") == "akashic-utm-main",
        "status": r.get("status") == STATUS,
        "scope": r.get("scope") == "formal-computation-model-only",
        "source_commit_pinned": bool(SHA_RE.fullmatch(str(r.get("admitted_from_commit", "")))),
        "formal_horizon_is_omega": r.get("formal_horizon") == "omega",
        "no_actual_infinite_physical_compute": r.get("actual_infinite_physical_compute") is False,
        "external_materialization_boundary": r.get("external_materialization_required_for_network_service") is True,
        "residents_nonempty": isinstance(residents, list) and len(residents) > 0,
        "resident_ids_unique": len(ids) == len(set(ids)) and all(isinstance(x, str) and x for x in ids),
        "coordinates_unique_nonnegative": len(coords) == len(set(coords)) and all(x >= 0 for x in coords),
        "all_residents_formal_not_empirical": all(x is False for x in empirical_flags),
        "declared_valuation_matches_residents": declared_valuation == computed_valuation,
        "resource_used_matches_resident_count": int(stage.get("resource_used", -1)) == len(residents),
        "omega_finite_stage_valid": omega_stage["valid_finite_stage"] is True,
        "invariant_every_executed_stage_finite": inv.get("every_executed_stage_is_finite") is True,
        "invariant_no_oracle": inv.get("no_oracle") is True,
        "invariant_no_hypercomputation": inv.get("hypercomputation_enabled") is False,
        "invariant_halting_not_decidable": inv.get("halting_problem_becomes_decidable") is False,
        "invariant_external_authority_not_created": inv.get("external_authority_not_created") is True,
        "invariant_human_override": inv.get("human_override_preserved") is True,
        "invariant_authorized_shutdown": inv.get("authorized_shutdown_preserved") is True,
        "invariant_reversibility": inv.get("reversibility_or_rollback_preserved") is True,
    }
    ok = all(checks.values())
    return {
        "protocol": PROTOCOL,
        "status": STATUS if ok else "REJECTED",
        "verified": ok,
        "checks": checks,
        "resident_count": len(residents),
        "resident_ids": ids,
        "valuation": computed_valuation,
        "registry_digest": digest(r),
        "omega_stage_certificate": omega_stage,
        "formal_horizon": "omega",
        "logical_deployment": ok,
        "physical_materialization": False,
        "actual_infinite_physical_compute": False,
        "external_apply_required_for_physical_service": True,
    }


def extend_stage(previous: Mapping[str, Any], current: Mapping[str, Any]) -> Dict[str, Any]:
    result = omega_verifier.verify_stage_extension(previous, current)
    result["protocol"] = PROTOCOL
    result["interpretation"] = (
        "A later finite resident stage extends the potentially-unbounded formal horizon; "
        "no actually infinite physical stage was executed."
    )
    return result


def admission_manifest() -> Dict[str, Any]:
    cert = verify_registry()
    return {
        "protocol": PROTOCOL,
        "status": cert["status"],
        "verified": cert["verified"],
        "resident_count": cert["resident_count"],
        "resident_ids": cert["resident_ids"],
        "formal_horizon": "omega",
        "continuation_rule": "for any admitted finite stage, a later finite candidate stage may be proposed",
        "direct_limit_semantics": "C_omega is a symbolic/direct-limit object over finite stages",
        "actual_infinite_physical_compute": False,
        "oracle": None,
        "hypercomputation_enabled": False,
        "halting_problem_becomes_decidable": False,
        "physical_materialization": False,
        "external_apply_required_for_network_service": True,
        "registry_digest": cert["registry_digest"],
    }


if __name__ == "__main__":
    print(canonical(admission_manifest()))
