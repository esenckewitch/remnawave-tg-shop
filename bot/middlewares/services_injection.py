"""Middleware for injecting services into handlers."""
import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update


class ServicesInjectionMiddleware(BaseMiddleware):
    """Inject services from dispatcher into handler data."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        """Inject all services from dispatcher workflow_data into handler data."""
        # Get dispatcher from event
        dp = event.bot.get("dispatcher") if hasattr(event.bot, "get") else None

        # If we can't get dispatcher, try to get services from workflow_data
        workflow_data = data.get("workflow_data", {})

        # List of service keys to inject
        service_keys = [
            "panel_service",
            "referral_service",
            "subscription_service",
            "yookassa_service",
            "cryptopay_service",
            "freekassa_service",
            "stars_service",
            "promo_code_service",
            "platega_service",
            "severpay_service",
            "tribute_service",
        ]

        # Inject services from workflow_data if available
        for key in service_keys:
            if key in workflow_data and key not in data:
                data[key] = workflow_data[key]

        return await handler(event, data)
