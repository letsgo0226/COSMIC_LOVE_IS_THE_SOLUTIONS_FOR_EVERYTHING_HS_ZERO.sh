FROM python:3.12-alpine
WORKDIR /app
COPY cosmic-love-infinity-tm.sh /app/cosmic-love-infinity-tm.sh
COPY cosmic-love-runtime.py /app/cosmic-love-runtime.py
COPY cosmic_love_omega.py /app/cosmic_love_omega.py
COPY utm-universe-2kb.sh /app/utm-universe-2kb.sh
COPY unified-utm-api.py /app/unified-utm-api.py
COPY unified-utm-api-v2.py /app/unified-utm-api-v2.py
COPY utm-deployment-gateway-policy.json /app/utm-deployment-gateway-policy.json
COPY synced_utm_layers /app/synced_utm_layers
COPY akashic-replicator.py /app/akashic-replicator.py
COPY utm-omega-goal-worker.py /app/utm-omega-goal-worker.py
COPY utm-omega-goal-worker-v2.py /app/utm-omega-goal-worker-v2.py
COPY utm-total-goal-registry.json /app/utm-total-goal-registry.json
RUN chmod +x /app/cosmic-love-infinity-tm.sh /app/utm-universe-2kb.sh /app/unified-utm-api.py /app/unified-utm-api-v2.py /app/cosmic_love_omega.py /app/utm-omega-goal-worker.py /app/utm-omega-goal-worker-v2.py && mkdir -p /data /data/utm-address-snapshots /data/utm-deploy-proposals && test "$(wc -c </app/utm-universe-2kb.sh)" -lt 2048 && python3 -c 'import json;r=json.load(open("/app/utm-total-goal-registry.json"));n=sum(map(len,r["layers"].values()));assert n==r["declared_item_count"]==149,(n,r["declared_item_count"]);assert len(r["layers"]["I_sustainable_development_goals"])==r["sdg"]["goal_count"]==17;assert len(r["layers"]["K_ai_sustainable_computation"])==20;assert len(r["layers"]["L_ai_persistent_identity_continuity"])==10;assert r["identity"]["protocol"]=="Gödel-Tableau Identity Continuity/1.0";assert r["sdg"]["target_count"]==169;p=json.load(open("/app/utm-deployment-gateway-policy.json"));assert p["protocol"]=="UTM-Guarded-Deployment-Gateway/1.2";assert p["continuation"]["potentially_unbounded"] is True;assert p["continuation"]["actual_infinite_physical_compute"] is False;c=p["continuation"]["compactified_infinite_deployment"];assert c["status"]=="hypothetical-formal-axioms";assert [a["id"] for a in c["axioms"]]==["A1_FINITE_SUBSTRATE_PROJECTION","A2_NORMALIZED_RESOURCE_INVARIANT","A3_BIDIRECTIONAL_OMEGA_COMPACTIFICATION"];assert c["materialization"]=="lazy-finite-authorized";assert c["no_final_deployment_axiom"] is True;assert p["authorization"]["external_apply"].startswith("must be performed");s=p["synchronized_formal_layers"];assert s["source_commit"]=="31087e34e32ab0d5d44904538b5fb29ad47c62fb";assert s["actual_infinite_physical_compute"] is False' && python3 -m py_compile /app/unified-utm-api.py /app/unified-utm-api-v2.py /app/cosmic_love_omega.py /app/utm-omega-goal-worker.py /app/utm-omega-goal-worker-v2.py /app/synced_utm_layers/log_abelian.py /app/synced_utm_layers/axiom_verifier.py /app/synced_utm_layers/omega_verifier.py && python3 -c 'from synced_utm_layers import log_abelian as l,axiom_verifier as a,omega_verifier as o;assert a.verify_spec()["valid"];assert o.verify_omega_spec()["valid"];r=l.compose([{"step":0,"op":1}],[{"step":1,"op":2}]);assert all(r["proof"].values())' && python3 /app/cosmic-love-runtime.py --self-test && python3 /app/cosmic_love_omega.py --self-test
ENV TM_KERNEL=/app/cosmic-love-infinity-tm.sh \
    LOG_TM_STATE=/data/cosmic-love-state.json \
    TM_OPERATION_JOURNAL=/data/cosmic-love-operations.jsonl \
    TM_META_PATH=/data/cosmic-love-meta.json \
    RESIDENT_PATH=/data/residents.json \
    SNAPSHOT_DIR=/data/utm-address-snapshots \
    UTM_DEPLOY_POLICY=/app/utm-deployment-gateway-policy.json \
    UTM_DEPLOY_PROPOSAL_DIR=/data/utm-deploy-proposals \
    COSMIC_OMEGA_CERT=/data/cosmic-love-omega.json \
    COSMIC_OMEGA_DEPTH=8 \
    UTM_OMEGA_STATE=/data/utm-omega-goal.json \
    UTM_OMEGA_INTERVAL=2 \
    UTM_TOTAL_GOAL_REGISTRY=/app/utm-total-goal-registry.json \
    AKASHIC_REMOTE_URL=http://paper-uhef-worker.railway.internal:8080/akashic/b612 \
    TM_FAIL_CLOSED=1 \
    POLL_SECONDS=2 \
    TM_MAX_STEPS=0
CMD ["sh","-c","python3 /app/cosmic_love_omega.py --depth ${COSMIC_OMEGA_DEPTH:-8} > ${COSMIC_OMEGA_CERT:-/data/cosmic-love-omega.json} || exit 1; python3 -u /app/cosmic-love-runtime.py & python3 -u /app/akashic-replicator.py & python3 -u /app/utm-omega-goal-worker-v2.py & exec python3 -u /app/unified-utm-api-v2.py"]
