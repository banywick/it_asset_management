#!/bin/sh

echo "=== DEBUG: Environment variables ==="
echo "POSTGRES_DB: $POSTGRES_DB"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_PASSWORD: $POSTGRES_PASSWORD"
echo "POSTGRES_HOST: $POSTGRES_HOST"
echo "POSTGRES_PORT: $POSTGRES_PORT"
echo "===================================="

echo "Waiting for PostgreSQL..."

echo "Waiting for PostgreSQL..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Apply database migrations
python manage.py migrate --noinput

# Create superuser if not exists
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
EOF

# Передаем переменные окружения в команду Django
export DJANGO_SETTINGS_MODULE=backend.settings

exec "$@"