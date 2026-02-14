import logging
from typing import List, Union
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery, User


class AdminFilter(Filter):

    def __init__(self, admin_ids: List[int]):
        self.admin_ids = admin_ids
        logging.info(f"AdminFilter initialized with admin_ids: {self.admin_ids}")

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        user_id = event.from_user.id if event.from_user else None
        result = False

        if not event.from_user:
            logging.warning(f"AdminFilter: No from_user in event")
            return False
        if not self.admin_ids:
            logging.warning(f"AdminFilter: admin_ids list is empty")
            return False

        result = event.from_user.id in self.admin_ids

        logging.info(f"AdminFilter check: user_id={user_id}, admin_ids={self.admin_ids}, result={result}")
        return result
