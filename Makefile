# Install dependencies using uv package manager
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev
# Launch local dev playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 💡 Try asking: What's the weather in San Francisco?                         |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'app' folder to interact with your agent.          |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# Deploy the agent remotely
# Usage: make backend [IAP=true] [PORT=8080] - Set IAP=true to enable Identity-Aware Proxy, PORT to specify container port
backend:
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run deploy hero \
		--source . \
		--memory "4Gi" \
		--project $$PROJECT_ID \
		--region "us-central1" \
		--no-allow-unauthenticated \
		--labels "created-by=adk" \
		--set-env-vars \
		"COMMIT_SHA=$(shell git rev-parse HEAD)" \
		$(if $(IAP),--iap) \
		$(if $(PORT),--port=$(PORT))

# Launch local development server with hot-reload
local-backend:
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload

# Set up development environment resources using Terraform
setup-dev-env:
		PROJECT_ID=$$(gcloud config get-value project) && \
		(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)
		
# 		# Minimal database initialization step
# 		DB_IP=$$(terraform -chdir=deployment/terraform output -raw hero_postgres_instance_ip 2>/dev/null || echo "")
# 		DB_PASS=$$(grep hr_db_password deployment/terraform/vars/env.tfvars | cut -d'=' -f2 | tr -d '" ')
# 		if [ -n "$$DB_IP" ]; then \
# 			sleep 30; \
# 			PGPASSWORD=$$DB_PASS psql -h $$DB_IP -U hero_user -d hero_human_resources -f deployment/database/schema.sql || true; \
# 			PGPASSWORD=$$DB_PASS psql -h $$DB_IP -U hero_user -d hero_human_resources -f deployment/database/tables/candidates.sql || true; \
# 			PGPASSWORD=$$DB_PASS psql -h $$DB_IP -U hero_user -d hero_human_resources -f deployment/database/tables/openings.sql || true; \
# 		fi

# Run unit and integration tests
test:
	uv run pytest tests/unit && uv run pytest tests/integration

# Run code quality checks (codespell, ruff, mypy)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .