FROM python:3.12-alpine
WORKDIR /app
COPY cosmic-love-infinity-tm.sh /app/cosmic-love-infinity-tm.sh
CMD ["sh","/app/cosmic-love-infinity-tm.sh"]
