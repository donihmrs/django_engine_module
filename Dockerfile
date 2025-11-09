# Gunakan base image Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies untuk build mysqlclient dan lainnya
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt dan install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code ke container
COPY . .

# (Opsional) Jalankan migrate di runtime, bukan di build
CMD ["sh", "-c", "python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"]

# Expose port Django
EXPOSE 8000
