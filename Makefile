run:
	uvicorn app.__main__:app --host 0.0.0.0 --port 8000 --reload

test:
	PYTHONPATH=. pytest app/tests/

# Os comandos agora leem a configuração do pyproject.toml
fmt:
	ruff check . --fix
	mypy app/
	black .

env:
	# gera .env.example
	echo "MODEL_PATH=/path/to/your/model.gguf" > .env.example
	echo "TWS_HOST=https://tws-master:31116" >> .env.example
	echo "TWS_USERNAME=your_tws_user" >> .env.example
	echo "TWS_PASSWORD=your_tws_password" >> .env.example
	echo "OPENROUTER_API_KEY=your_openrouter_key" >> .env.example
	echo "OPENAI_API_KEY=" >> .env.example
	echo "TWS_MOCK_MODE=True" >> .env.example
