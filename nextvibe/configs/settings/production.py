from .base import *

DEBUG = False

# 반드시 도메인/IP 지정
# ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["your-domain.com"])

# --- 데이터베이스: postgre ---
DATABASES = {
    "default": env.db(  # 예: DATABASE_URL=postgres://user:pass@host:5432/db
        "DATABASE_URL",
        default="postgres://user:pass@localhost:5432/nextvibe",
    )
}

# --- 캐시: Redis 예시 ---
# 예: REDIS_URL=redis://localhost:6379/1
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/1"),
        "TIMEOUT": None,
        "OPTIONS": {"client_class": "django_redis.client.DefaultClient"},
    }
}

# CORS: 운영에서는 전체 허용 금지, 필요한 오리진만
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ORIGIN_ALLOW_ALL", default=False)
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[
    "https://your-frontend.com",
])
