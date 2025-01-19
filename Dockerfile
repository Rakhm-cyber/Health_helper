FROM python:3.11

WORKDIR /bot

COPY . .

RUN pip install pyinstaller && pip install --no-cache-dir -r requirements.txt && pyinstaller --onefile main.py

FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=build /build/dist/main .

CMD ["./main"]
