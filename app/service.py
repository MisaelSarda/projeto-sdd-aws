"""
Camada de serviços e persistência em memória para a gestão de tarefas.
Implementação isolada da camada de transporte HTTP para facilitar testes unitários.
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate


class TaskService:
    def __init__(self) -> None:
        self._tasks: Dict[int, TaskResponse] = {}
        self._current_id: int = 0

    def create_task(self, data: TaskCreate) -> TaskResponse:
        self._current_id += 1
        now = datetime.now(timezone.utc)
        task = TaskResponse(
            id=self._current_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._tasks[self._current_id] = task
        return task

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[TaskResponse]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.id)

    def get_task(self, task_id: int) -> Optional[TaskResponse]:
        return self._tasks.get(task_id)

    def update_task(self, task_id: int, data: TaskUpdate) -> Optional[TaskResponse]:
        task = self._tasks.get(task_id)
        if not task:
            return None

        updated_dict = task.model_dump()
        if data.title is not None:
            updated_dict["title"] = data.title
        if data.description is not None:
            updated_dict["description"] = data.description
        if data.priority is not None:
            updated_dict["priority"] = data.priority
        if data.status is not None:
            updated_dict["status"] = data.status

        updated_dict["updated_at"] = datetime.now(timezone.utc)
        updated_task = TaskResponse(**updated_dict)
        self._tasks[task_id] = updated_task
        return updated_task

    def delete_task(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def reset_state(self) -> None:
        """Utilizado para isolamento entre testes unitários."""
        self._tasks.clear()
        self._current_id = 0


task_service = TaskService()
