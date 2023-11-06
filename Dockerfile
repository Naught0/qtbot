FROM python:3.8-alpine
WORKDIR /qtbot
COPY . .
ENV PYTHONUNBUFFERED=1
RUN apk add libffi-dev gcc libc-dev build-base jpeg-dev zlib-dev
RUN pip install -r requirements.txt

CMD ["python3", "launcher.py"]
