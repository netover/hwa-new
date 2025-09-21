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
	echo "TWS_HOST= https://tws-master:31116" > .env
	echo "OPENROUTER_API_KEY= sua-chave-openrouter" >> .env
	echo "MODEL_PATH=/models/gemma-2b-it-GGUF.Q4_K_M.gguf" >> .env
