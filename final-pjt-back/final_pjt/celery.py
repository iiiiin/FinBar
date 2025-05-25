# final_pjt/celery.py

import os
from celery import Celery

# 1. Django 설정 모듈 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'final_pjt.settings')

# 2. Celery 앱 생성 (프로젝트 이름 사용)
app = Celery('final_pjt')

# 3. settings.py의 CELERY_ 네임스페이스 하위 키 읽어오기
#    ex) CELERY_BROKER_URL, CELERY_RESULT_BACKEND 등
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. 각 앱의 tasks.py 자동 검색
app.autodiscover_tasks()
