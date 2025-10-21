APP_NAME=venue-accesses-app

build: ## Build the container
	docker build . -t venue-accesses-app

run: ## Run containers
	docker run -d --name venue-accesses-app -p 8085:80 venue-accesses-app

test:## Run code test
	pytest