FROM python:3.12-alpine
WORKDIR /app
COPY cosmic-love-infinity-tm.sh /app/cosmic-love-infinity-tm.sh
COPY cosmic-love-runtime.py /app/cosmic-love-runtime.py
RUN chmod +x /app/cosmic-love-infinity-tm.sh && mkdir -p /data && python3 /app/cosmic-love-runtime.py --self-test
ENV TM_KERNEL=/app/cosmic-love-infinity-tm.sh \
    LOG_TM_STATE=/data/cosmic-love-state.json \
    TM_OPERATION_JOURNAL=/data/cosmic-love-operations.jsonl \
    TM_META_PATH=/data/cosmic-love-meta.json \
    TM_FAIL_CLOSED=1 \
    POLL_SECONDS=2 \
    TM_MAX_STEPS=0
CMD ["python3","-u","/app/cosmic-love-runtime.py"]
