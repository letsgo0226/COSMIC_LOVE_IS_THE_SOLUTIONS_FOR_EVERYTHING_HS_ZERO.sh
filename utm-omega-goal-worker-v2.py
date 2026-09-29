#!/usr/bin/env python3
"""Registry overlay for the deployed UTM-Omega continuation worker.

Keeps the existing dovetail engine and continuation checkpoint semantics while
replacing its goal registry with UTM-Omega-Total-Goal-Kernel/2.0. Existing
stage progress is migrated in place when the protocol is unchanged.
"""
import importlib.util, json, os, sys
from pathlib import Path

BASE=Path(__file__).with_name("utm-omega-goal-worker.py")
REGISTRY_PATH=Path(os.getenv("UTM_TOTAL_GOAL_REGISTRY",Path(__file__).with_name("utm-total-goal-registry.json")))

spec=importlib.util.spec_from_file_location("utm_omega_core",BASE)
core=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=core
spec.loader.exec_module(core)
REG=json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
core.GOALS=REG["layers"]

_orig_default=core.default_state
_orig_load=core.load_state
_orig_publish=core.publish

def goal_registry():
    return {
        "kernel":REG["kernel"],
        "world_id":REG["world_id"],
        "layers":REG["layers"],
        "goal_count":sum(len(v) for v in REG["layers"].values()),
        "sdg_goal_count":REG["sdg"]["goal_count"],
        "sdg_target_count":REG["sdg"]["target_count"],
        "hard_constraints":REG["hard_constraints"],
        "sdg":REG["sdg"],
        "semantics":REG["semantics"],
        "P_target_goal":1,
        "C_target":0,
        "P_empirical_hat":None,
        "A_target":1,
        "G_target":1,
    }

def inject(state):
    state["goal_registry"]=goal_registry()
    state["goal_registry"]["C_target"]=1 if state.get("best_observed") else 0
    state["total_goal_kernel"]=REG["kernel"]
    state["declared_item_count"]=REG["declared_item_count"]
    state["sdg_integration"]={"goals":17,"targets":169,"crosswalk_semantics":REG["sdg"]["crosswalk_semantics"]}
    state["boundary"]=list(dict.fromkeys(list(state.get("boundary",[]))+REG.get("boundaries",[])))
    return state

def default_state():
    return inject(_orig_default())

def load_state():
    return inject(_orig_load())

def publish(state):
    _orig_publish(state)
    n=int(state.get("stage",0))
    if n<=3 or n%50==0:
        print(json.dumps({"event":"UTM_OMEGA_RESIDENT_PUBLISHED","agent_id":core.AGENT_ID,"stage":n,"kernel":REG["kernel"],"declared_item_count":REG["declared_item_count"],"sdg_goal_count":REG["sdg"]["goal_count"],"sdg_target_count":REG["sdg"]["target_count"],"C_target":state["goal_registry"]["C_target"],"actual_infinite_physical_compute":False},separators=(",",":")),flush=True)

core.default_state=default_state
core.load_state=load_state
core.publish=publish
print(json.dumps({"event":"UTM_OMEGA_TOTAL_REGISTRY_READY","kernel":REG["kernel"],"declared_item_count":REG["declared_item_count"],"layers":len(REG["layers"]),"sdg_goal_count":REG["sdg"]["goal_count"],"sdg_target_count":REG["sdg"]["target_count"],"potentially_unbounded":True,"actual_infinite_physical_compute":False},separators=(",",":")),flush=True)
core.main()
