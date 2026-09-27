FROM python:3.12-alpine
WORKDIR /app
COPY cosmic-love-infinity-tm.sh /app/cosmic-love-infinity-tm.sh
COPY cosmic-love-runtime.py /app/cosmic-love-runtime.py
COPY utm-universe-2kb.sh /app/utm-universe-2kb.sh
COPY akashic-replicator.py /app/akashic-replicator.py
RUN chmod +x /app/cosmic-love-infinity-tm.sh /app/utm-universe-2kb.sh && mkdir -p /data && test "$(wc -c </app/utm-universe-2kb.sh)" -lt 2048 && python3 /app/cosmic-love-runtime.py --self-test
ENV TM_KERNEL=/app/cosmic-love-infinity-tm.sh \
    LOG_TM_STATE=/data/cosmic-love-state.json \
    TM_OPERATION_JOURNAL=/data/cosmic-love-operations.jsonl \
    TM_META_PATH=/data/cosmic-love-meta.json \
    RESIDENT_PATH=/data/residents.json \
    AKASHIC_REMOTE_URL=http://paper-uhef-worker.railway.internal:8080/akashic/b612 \
    TM_FAIL_CLOSED=1 \
    POLL_SECONDS=2 \
    TM_MAX_STEPS=0
CMD ["sh","-c","python3 -u /app/cosmic-love-runtime.py & python3 -u /app/akashic-replicator.py & exec sh /app/utm-universe-2kb.sh"]
