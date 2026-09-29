FROM python:3.12-alpine
WORKDIR /app
COPY cosmic-love-infinity-tm.sh /app/cosmic-love-infinity-tm.sh
COPY cosmic-love-runtime.py /app/cosmic-love-runtime.py
COPY cosmic_love_omega.py /app/cosmic_love_omega.py
COPY utm-universe-2kb.sh /app/utm-universe-2kb.sh
COPY unified-utm-api.py /app/unified-utm-api.py
COPY akashic-replicator.py /app/akashic-replicator.py
COPY utm-omega-goal-worker.py /app/utm-omega-goal-worker.py
COPY utm-omega-goal-worker-v2.py /app/utm-omega-goal-worker-v2.py
COPY utm-total-goal-registry.json /app/utm-total-goal-registry.json
RUN chmod +x /app/cosmic-love-infinity-tm.sh /app/utm-universe-2kb.sh /app/unified-utm-api.py /app/cosmic_love_omega.py /app/utm-omega-goal-worker.py /app/utm-omega-goal-worker-v2.py && mkdir -p /data /data/utm-address-snapshots && test "$(wc -c </app/utm-universe-2kb.sh)" -lt 2048 && python3 -m py_compile /app/unified-utm-api.py /app/cosmic_love_omega.py /app/utm-omega-goal-worker.py /app/utm-omega-goal-worker-v2.py && python3 /app/cosmic-love-runtime.py --self-test && python3 /app/cosmic_love_omega.py --self-test
ENV TM_KERNEL=/app/cosmic-love-infinity-tm.sh \
    LOG_TM_STATE=/data/cosmic-love-state.json \
    TM_OPERATION_JOURNAL=/data/cosmic-love-operations.jsonl \
    TM_META_PATH=/data/cosmic-love-meta.json \
    RESIDENT_PATH=/data/residents.json \
    SNAPSHOT_DIR=/data/utm-address-snapshots \
    COSMIC_OMEGA_CERT=/data/cosmic-love-omega.json \
    COSMIC_OMEGA_DEPTH=8 \
    UTM_OMEGA_STATE=/data/utm-omega-goal.json \
    UTM_OMEGA_INTERVAL=2 \
    UTM_TOTAL_GOAL_REGISTRY=/app/utm-total-goal-registry.json \
    AKASHIC_REMOTE_URL=http://paper-uhef-worker.railway.internal:8080/akashic/b612 \
    TM_FAIL_CLOSED=1 \
    POLL_SECONDS=2 \
    TM_MAX_STEPS=0
CMD ["sh","-c","python3 /app/cosmic_love_omega.py --depth ${COSMIC_OMEGA_DEPTH:-8} > ${COSMIC_OMEGA_CERT:-/data/cosmic-love-omega.json} || exit 1; python3 -u /app/cosmic-love-runtime.py & python3 -u /app/akashic-replicator.py & python3 -u /app/utm-omega-goal-worker-v2.py & exec python3 -u /app/unified-utm-api.py"]
