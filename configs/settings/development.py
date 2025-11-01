from .base import *
import environ

environ.Env.read_env(os.path.join(BASE_DIR, 'env', '.env.dev'))

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}

# CACHES = {
#    'default': env.cache(),
#}

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

CORS_ORIGIN_ALLOW_ALL = True