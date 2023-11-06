FROM python:3.8-alpine
WORKDIR /qtbot
COPY . .
ENV PYTHONUNBUFFERED=1
RUN apk add libffi-dev gcc libc-dev build-base jpeg-dev zlib-dev
RUN pip install -r requirements.txt
RUN python3 -c 'import nltk; nltk.download("stopwords")'
CMD ["python3", "launcher.py"]
