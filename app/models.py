"""
Modelos de dados (Schemas Pydantic) estritamente derivados do contrato OpenAPI (docs/openapi.yaml).
Garante a conformidade da abordagem Spec-Driven Development (SDD).
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Título da tarefa",
        json_schema_extra={"example": "Configurar EC2 na AWS"}
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Descrição detalhada",
        json_schema_extra={"example": "Subir instância Ubuntu 24.04 e instalar Docker"}
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Nível de prioridade"
    )


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str


class AppInfoResponse(BaseModel):
    application: str
    version: str
    methodology: str
    environment: str


class ErrorResponse(BaseModel):
    detail: str
