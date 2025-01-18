dev:
	docker compose down postgres -v
	docker compose up postgres -d
migrate:
	migrate -database 'postgres://postgres:1@localhost:5432/1?sslmode=disable' -path ./migrations up
run:
	python main.py