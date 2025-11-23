from .base import *
import environ

environ.Env.read_env(os.path.join(BASE_DIR, 'env', '.env.dev'))

DATABASES = {    
        "default": env.db_url(
            "DATABASE_URL",
            default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}

CACHES = {
    'default': env.cache(),
}

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

CORS_ORIGIN_ALLOW_ALL = True

USE_INMEMORY = env("CHANNEL_LAYER", default="redis") == "memory"

if USE_INMEMORY:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
    
else:
    REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        }
    }