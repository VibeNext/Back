# 환경변수 DJANGO_ENV 값에 따라 settings 모듈 선택
import os

env = os.getenv("DJANGO_ENV", "development").lower()
if env == "production":
    from .production import *  # noqa
else:
    from .development import *  # noqa
