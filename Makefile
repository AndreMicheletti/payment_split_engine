
run:
	poetry run python manage.py runserver

migrate:
	poetry run python manage.py migrate

make-migrations:
	poetry run python manage.py makemigrations

test:
	poetry run python manage.py test

black:
	poetry run black .
