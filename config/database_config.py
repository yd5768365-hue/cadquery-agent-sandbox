import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://cae_user:cae_pass_2024@postgres:5432/cae_platform')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
