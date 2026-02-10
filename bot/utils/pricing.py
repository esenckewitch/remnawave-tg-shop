from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from config.settings import Settings


@dataclass(frozen=True)
class UserPrices:
    subscription_options: Dict[int, float]
    stars_subscription_options: Dict[int, int]
    traffic_packages: Dict[float, float]
    stars_traffic_packages: Dict[float, int]


def is_grandfathered(settings: Settings, registration_date: Optional[datetime]) -> bool:
    """True if the user should see old (grandfathered) prices."""
    cutoff = settings.price_change_date_parsed
    if cutoff is None:
        return True
    if registration_date is None:
        return False
    return registration_date < cutoff


def get_user_prices(settings: Settings, registration_date: Optional[datetime]) -> UserPrices:
    """Return the correct price set for a user based on their registration date."""
    if is_grandfathered(settings, registration_date):
        return UserPrices(
            subscription_options=settings.subscription_options,
            stars_subscription_options=settings.stars_subscription_options,
            traffic_packages=settings.traffic_packages,
            stars_traffic_packages=settings.stars_traffic_packages,
        )
    return UserPrices(
        subscription_options=settings.subscription_options_new,
        stars_subscription_options=settings.stars_subscription_options_new,
        traffic_packages=settings.traffic_packages_new,
        stars_traffic_packages=settings.stars_traffic_packages_new,
    )
