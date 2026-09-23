from time import perf_counter

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.cache.redis_cache import RedisCacheBackend
from app.repositories.category import CategoryRepository
from app.schemas.category import (
    CategoryCreateSchema,
    CategorySchema,
    CategoryUpdateSchema,
)

class CategoryService:
    def __init__(
        self,
        db: Session,
        cache_redis_url: str,
        cache_ttl_seconds: int,
        cache_categories_key: str,
    ) -> None:
        self.db = db
        self.category_repository = CategoryRepository(db)
        self.cache = RedisCacheBackend(cache_redis_url, cache_ttl_seconds)
        self.cache_categories_key = cache_categories_key

    def list_categories(self) -> list[CategorySchema]:
        start_time = perf_counter()
        cached_categories = self.cache.get(self.cache_categories_key)

        if cached_categories is not None:
            return [
                CategorySchema.model_validate(category)
                for category in cached_categories
            ]

        categories_orm = self.category_repository.get_all()
        categories = [
            CategorySchema.model_validate(category)
            for category in categories_orm
        ]

        categories_for_cache = [
            category.model_dump(mode="json")
            for category in categories
        ]

        self.cache.set(
            self.cache_categories_key,
            categories_for_cache,
        )
        return categories

    def create_category(self, category_create: CategoryCreateSchema) -> CategorySchema:
        category_orm = self.category_repository.create(name=category_create.name)
        self.db.commit()
        self.db.refresh(category_orm)
        self.cache.delete(self.cache_categories_key)
        return CategorySchema.model_validate(category_orm)

    def update_category(
        self,
        category_id: str,
        category_update: CategoryUpdateSchema,
    ) -> CategorySchema:
        category_for_update = self.category_repository.get_by_id(category_id=category_id)

        if category_for_update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        if category_update.name is not None:
            category_for_update.name = category_update.name

        self.db.commit()
        self.db.refresh(category_for_update)
        self.cache.delete(self.cache_categories_key)
        return CategorySchema.model_validate(category_for_update)

    def delete_category(self, category_id: str) -> None:
        category_for_delete = self.category_repository.get_by_id(category_id=category_id)

        if category_for_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        self.category_repository.delete(category_for_delete)
        self.db.commit()
        self.cache.delete(self.cache_categories_key)
