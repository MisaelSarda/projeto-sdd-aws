"""
Suíte de testes unitários automatizados.
Garante a cobertura de código exigida pelo Quality Gate do SonarQube (>80%).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.service import task_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_state():
    """Roda antes de cada teste para isolar os dados."""
    task_service.reset_state()
    yield
    task_service.reset_state()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data


def test_get_info():
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "Task & Service Health API"
    assert data["methodology"] == "Spec-Driven Development (SDD)"
    assert data["version"] == "1.0.0"


def test_create_task_success():
    payload = {
        "title": "Configurar EC2 na AWS",
        "description": "Subir instância Ubuntu e liberar porta 80",
        "priority": "HIGH",
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["priority"] == "HIGH"
    assert data["status"] == "PENDING"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_validation_error():
    # Título com menos de 3 caracteres (regra estrita do SDD)
    payload = {"title": "AB"}
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422


def test_list_tasks_and_filter():
    # Cadastrar duas tarefas
    client.post("/api/v1/tasks", json={"title": "Tarefa 1", "priority": "LOW"})
    client.post("/api/v1/tasks", json={"title": "Tarefa 2", "priority": "HIGH"})

    # Listar todas
    resp_all = client.get("/api/v1/tasks")
    assert resp_all.status_code == 200
    assert len(resp_all.json()) == 2

    # Filtrar por status PENDING
    resp_filtered = client.get("/api/v1/tasks?status=PENDING")
    assert resp_filtered.status_code == 200
    assert len(resp_filtered.json()) == 2

    # Filtrar por status COMPLETED (deve vir vazio)
    resp_completed = client.get("/api/v1/tasks?status=COMPLETED")
    assert resp_completed.status_code == 200
    assert len(resp_completed.json()) == 0


def test_get_task_by_id():
    created = client.post(
        "/api/v1/tasks", json={"title": "Configurar SonarCloud"}
    ).json()
    task_id = created["id"]

    # Busca com sucesso
    resp_found = client.get(f"/api/v1/tasks/{task_id}")
    assert resp_found.status_code == 200
    assert resp_found.json()["title"] == "Configurar SonarCloud"

    # Busca inexistente
    resp_not_found = client.get("/api/v1/tasks/9999")
    assert resp_not_found.status_code == 404
    assert "não encontrada" in resp_not_found.json()["detail"]


def test_update_task():
    created = client.post(
        "/api/v1/tasks", json={"title": "Tarefa Inicial", "priority": "LOW"}
    ).json()
    task_id = created["id"]

    update_payload = {
        "title": "Tarefa Atualizada com Sucesso",
        "priority": "HIGH",
        "status": "COMPLETED",
    }
    resp_update = client.put(f"/api/v1/tasks/{task_id}", json=update_payload)
    assert resp_update.status_code == 200
    data = resp_update.json()
    assert data["title"] == update_payload["title"]
    assert data["priority"] == "HIGH"
    assert data["status"] == "COMPLETED"

    # Atualizar ID inexistente
    resp_update_404 = client.put("/api/v1/tasks/9999", json={"title": "Inexistente"})
    assert resp_update_404.status_code == 404


def test_delete_task():
    created = client.post(
        "/api/v1/tasks", json={"title": "Tarefa para Deleção"}
    ).json()
    task_id = created["id"]

    # Deleção bem-sucedida (204 No Content)
    resp_delete = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp_delete.status_code == 204

    # Confirmação de que não existe mais
    resp_check = client.get(f"/api/v1/tasks/{task_id}")
    assert resp_check.status_code == 404

    # Tentar deletar novamente
    resp_delete_again = client.delete(f"/api/v1/tasks/{task_id}")
    assert resp_delete_again.status_code == 404
