
import os

os.environ.setdefault("JWT_SECRET_KEY", "chave-temporaria-apenas-para-testes")
os.environ.setdefault("API_USERNAME", "admin")
os.environ.setdefault("API_PASSWORD", "senha-temporaria-de-testes")

from fastapi.testclient import TestClient

from main import app


def test_rota_inicial():
    with TestClient(app) as client:
        resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "API Bancária funcionando!"}

def test_extrato_sem_token_retorna_401():
    with TestClient(app) as client:
        resposta = client.get("/accounts/1/statement")

    assert resposta.status_code == 401

def test_transacao_com_valor_zero_retorna_422():
    with TestClient(app) as client:
        resposta_token = client.post(
            "/token",
            data={
                "username": os.environ["API_USERNAME"],
                "password": os.environ["API_PASSWORD"],
            },
        )

        assert resposta_token.status_code == 200

        token = resposta_token.json()["access_token"]

        resposta = client.post(
            "/accounts/1/transactions",
            headers={"Authorization": f"Bearer {token}"},
            json={"tipo": "deposito", "valor": 0},
        )

    assert resposta.status_code == 422
