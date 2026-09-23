from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.cache.redis_cache import RedisCacheBackend
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreateSchema, TaskSchema, TaskUpdateSchema


class TaskService:
    def __init__(self, db: Session, cache_redis_url: str, cache_ttl_seconds: int, cache_tasks_key: str ) -> None:
        self.db = db
        self.task_repository = TaskRepository(db)
        self.cache = RedisCacheBackend(cache_redis_url, cache_ttl_seconds)
        self.cache_tasks_key = cache_tasks_key

    def list_tasks(self) -> list[TaskSchema]:
        # 1. Проверяем Redis
        cached_tasks = self.cache.get(self.cache_tasks_key)

        # 2. Если есть — возвращаем из Redis
        if cached_tasks is not None:
            return [
                TaskSchema.model_validate(task)
                for task in cached_tasks
            ]

        # 3. Только если Redis пуст — идём в БД
        tasks_orm = self.task_repository.get_all()

        tasks = [
            TaskSchema.model_validate(task)
            for task in tasks_orm
        ]

        # 4. Pydantic-модели превращаем в JSON-совместимые dict
        tasks_for_cache = [
            task.model_dump(mode="json")
            for task in tasks
        ]

        # 5. Сохраняем в Redis чтобы закешировать
        self.cache.set(
            self.cache_tasks_key,
            tasks_for_cache,
        )

        return tasks

    def create_task(self, task_create: TaskCreateSchema) -> TaskSchema:
        task_orm = self.task_repository.create(title=task_create.title)
        self.db.commit()
        self.db.refresh(task_orm)
        # БД успешно изменилась → старый кэш больше не актуален
        self.cache.delete(self.cache_tasks_key)
        return TaskSchema.model_validate(task_orm)

    def update_task(self, task_id: str, task_update: TaskUpdateSchema) -> TaskSchema:
        task_for_update = self.task_repository.get_by_id(task_id=task_id)

        if task_for_update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if task_update.title is not None:
            task_for_update.title = task_update.title

        if task_update.completed is not None:
            task_for_update.completed = task_update.completed

        self.db.commit()
        self.db.refresh(task_for_update)
        self.cache.delete(self.cache_tasks_key)

        return TaskSchema.model_validate(task_for_update)

    def delete_task(self, task_id: str) -> None:
        task_for_delete = self.task_repository.get_by_id(task_id=task_id)

        if task_for_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        self.task_repository.delete(task_for_delete)
        self.db.commit()
        self.cache.delete(self.cache_tasks_key)
