# 1. 베이스 이미지
FROM python:3.10-slim

# 2. 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 작업 디렉토리 설정
WORKDIR /back

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. 종속성 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 5. 전체 코드 복사
COPY . .

# 6. 기본 실행 명령 (개발용 runserver 또는 운영용 gunicorn 선택)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
# 배포 시 아래 설정으로 변경 고려
# CMD ["gunicorn", "manage.py", "--bind", "0.0.0.0:8080"]
