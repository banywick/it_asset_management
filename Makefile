.PHONY: help build-dev build-prod up-dev up-prod down-dev down-prod logs-dev logs-prod shell-backend migrate createsuperuser clean

help:
	@echo "Available commands:"
	@echo "  make up-dev        - Запуск в режиме разработки"
	@echo "  make up-prod       - Запуск в режиме продакшена"
	@echo "  make build-dev     - Сборка образов для разработки"
	@echo "  make build-prod    - Сборка образов для продакшена"
	@echo "  make down-dev      - Остановка контейнеров разработки"
	@echo "  make down-prod     - Остановка контейнеров продакшена"
	@echo "  make logs-dev      - Просмотр логов разработки"
	@echo "  make logs-prod     - Просмотр логов продакшена"
	@echo "  make shell-backend - Вход в контейнер бэкенда"
	@echo "  make migrate       - Применение миграций"
	@echo "  make createsuperuser - Создание суперпользователя"
	@echo "  make clean         - Очистка всех контейнеров и томов"

up-dev:
	docker-compose up

up-prod:
	docker-compose -f docker-compose.prod.yml up -d

build-dev:
	docker-compose build

build-prod:
	docker-compose -f docker-compose.prod.yml build

down-dev:
	docker-compose down

down-prod:
	docker-compose -f docker-compose.prod.yml down

logs-dev:
	docker-compose logs -f

logs-prod:
	docker-compose -f docker-compose.prod.yml logs -f

shell-backend:
	docker-compose exec backend bash

migrate:
	docker-compose exec backend python manage.py migrate

createsuperuser:
	docker-compose exec backend python manage.py createsuperuser

clean:
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v
	docker system prune -f