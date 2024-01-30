FROM python:3.10-alpine
WORKDIR /qtbot
COPY . .
ENV PYTHONUNBUFFERED=1
RUN apk add libffi-dev gcc libc-dev build-base jpeg-dev zlib-dev cairo
RUN pip install -r requirements.txt
RUN python3 -c 'import nltk; nltk.download("stopwords")'
RUN prisma generate
CMD ["python3", "launcher.py"]
