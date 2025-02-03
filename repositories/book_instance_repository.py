from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import Book, BookInstance
from repositories.abstract_repositories import AbstractBookInstanceRepository


class BookInstanceRepository(AbstractBookInstanceRepository):
    async def create_new_book_instance(self, book: Book, new_book_instance: BookInstance) -> BookInstance:
        self.db.add(new_book_instance)

        book.quantity += 1
        book.available_for_loan += 1

        await self.db.commit()
        await self.db.refresh(new_book_instance)

        return new_book_instance

    async def get_book_instance_by_id(self, book_instance_id: int) -> BookInstance | None:
        result = await self.db.execute(
            select(BookInstance)
            .options(joinedload(BookInstance.book))
            .where(BookInstance.id == book_instance_id)
        )
        book_instance = result.unique().scalars().first()

        return book_instance if book_instance else None

    async def get_all_instances_by_book_id(self, book_id: int) -> Book | None:
        result = await self.db.execute(
            select(Book)
            .options(joinedload(Book.authors), joinedload(Book.genres), joinedload(Book.instances))
            .where(Book.id == book_id)
        )
        book_with_instances = result.unique().scalars().first()

        return book_with_instances if book_with_instances else None

    async def update_book_instance(self, book_item_to_update):
        pass

    async def delete_book_instance(self, book_item_to_delete):
        pass
