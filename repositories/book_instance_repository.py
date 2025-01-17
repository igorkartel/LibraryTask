from models import BookInstance
from repositories.abstract_repositories import AbstractBookInstanceRepository


class BookInstanceRepository(AbstractBookInstanceRepository):
    async def create_new_book_instance(self, new_book_instance: BookInstance) -> BookInstance:
        self.db.add(new_book_instance)
        await self.db.commit()
        await self.db.refresh(new_book_instance)

        return new_book_instance

    async def get_book_instance_by_id(self, book_instance_id: int) -> BookInstance | None:
        pass

    async def get_all_instances_by_book_title(self, request_payload):
        pass

    async def update_book_instance(self, book_item_to_update):
        pass

    async def delete_book_instance(self, book_item_to_delete):
        pass
