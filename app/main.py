"""
Aplicação Principal FastAPI - Task & Service Health API.
Desenvolvida segundo a especificação formal em docs/openapi.yaml (SDD).
"""
import os
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Path, Query, status
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    AppInfoResponse,
    ErrorResponse,
    HealthResponse,
    TaskCreate,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)
from app.service import task_service

app = FastAPI(
    title="Task & Service Health API",
    description=(
        "API RESTful desenvolvida com base na técnica de engenharia "
        "Spec-Driven Development (SDD) para trabalho prático de DevOps e AWS Cloud."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configuração de CORS para permitir consumo de qualquer frontend ou testes de integração
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Monitoramento"],
    summary="Health Check do Sistema",
)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version="1.0.0",
    )


@app.get(
    "/api/v1/info",
    response_model=AppInfoResponse,
    tags=["Diagnóstico"],
    summary="Informações da Aplicação e do Ambiente",
)
def get_info() -> AppInfoResponse:
    env = os.getenv("APP_ENV", "production")
    return AppInfoResponse(
        application="Task & Service Health API",
        version="1.0.0",
        methodology="Spec-Driven Development (SDD)",
        environment=env,
    )


@app.get(
    "/api/v1/tasks",
    response_model=List[TaskResponse],
    tags=["Tarefas"],
    summary="Listar tarefas",
)
def list_tasks(
    status_filter: Optional[TaskStatus] = Query(
        None,
        alias="status",
        description="Filtro opcional por status",
    )
) -> List[TaskResponse]:
    return task_service.list_tasks(status=status_filter)


@app.post(
    "/api/v1/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tarefas"],
    summary="Criar nova tarefa",
)
def create_task(task_in: TaskCreate) -> TaskResponse:
    return task_service.create_task(task_in)


@app.get(
    "/api/v1/tasks/{id}",
    response_model=TaskResponse,
    responses={404: {"model": ErrorResponse}},
    tags=["Tarefas"],
    summary="Obter tarefa por ID",
)
def get_task(
    task_id: int = Path(..., alias="id", description="ID da tarefa")
) -> TaskResponse:
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarefa com ID {task_id} não encontrada.",
        )
    return task


@app.put(
    "/api/v1/tasks/{id}",
    response_model=TaskResponse,
    responses={404: {"model": ErrorResponse}},
    tags=["Tarefas"],
    summary="Atualizar tarefa",
)
def update_task(
    task_in: TaskUpdate,
    task_id: int = Path(..., alias="id", description="ID da tarefa"),
) -> TaskResponse:
    updated = task_service.update_task(task_id, task_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarefa com ID {task_id} não encontrada.",
        )
    return updated


@app.delete(
    "/api/v1/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    tags=["Tarefas"],
    summary="Excluir tarefa",
)
def delete_task(
    task_id: int = Path(..., alias="id", description="ID da tarefa")
) -> None:
    deleted = task_service.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarefa com ID {task_id} não encontrada.",
        )
    return None
