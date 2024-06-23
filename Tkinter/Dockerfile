FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    python3-tk \
    xvfb \
    && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x16 & python main.py"]
