FROM python:3.12-alpine
WORKDIR /app
COPY one-liner-2kb.sh /app/one-liner-2kb.sh
CMD ["sh","/app/one-liner-2kb.sh"]
