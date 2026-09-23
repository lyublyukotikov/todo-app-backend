from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.session import get_db
from app.services.category import CategoryService
from app.services.task import TaskService


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """Функция для инъекции зависимостей TaskService"""
    settings = get_settings()
    return TaskService(
        db=db,
        cache_redis_url=settings.redis_url,
        cache_ttl_seconds=settings.cache_ttl_seconds,
        cache_tasks_key=settings.cache_tasks_key,
    )


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    """Функция для инъекции зависимостей CategoryService"""
    settings = get_settings()
    return CategoryService(
        db=db,
        cache_redis_url=settings.redis_url,
        cache_ttl_seconds=settings.cache_ttl_seconds,
        cache_categories_key=settings.cache_categories_key,
    )
