FROM python:3.11-slim

# System deps required by pygame (runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libx11-6 libxext6 libxrender1 libxtst6 libxi6 libxrandr2 \
    libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 \
    libfreetype6 libjpeg62-turbo libpng16-16 \
    git bash ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "src.main"]
