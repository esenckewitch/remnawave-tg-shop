import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from sqlalchemy import select, and_, not_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import WinbackDiscount, Subscription, User, Payment


async def get_active_discount_for_user(
    session: AsyncSession, user_id: int
) -> Optional[WinbackDiscount]:
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(WinbackDiscount)
        .where(
            WinbackDiscount.user_id == user_id,
            WinbackDiscount.redeemed_at.is_(None),
            WinbackDiscount.expires_at > now,
        )
        .order_by(WinbackDiscount.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_winback_discount(
    session: AsyncSession,
    user_id: int,
    discount_percent: int = 15,
    validity_days: int = 7,
) -> WinbackDiscount:
    discount = WinbackDiscount(
        user_id=user_id,
        discount_percent=discount_percent,
        expires_at=datetime.now(timezone.utc) + timedelta(days=validity_days),
    )
    session.add(discount)
    return discount


async def mark_discount_redeemed(
    session: AsyncSession,
    discount_id: int,
    payment_id: Optional[int] = None,
) -> None:
    result = await session.execute(
        select(WinbackDiscount).where(WinbackDiscount.discount_id == discount_id)
    )
    discount = result.scalar_one_or_none()
    if discount:
        discount.redeemed_at = datetime.now(timezone.utc)
        if payment_id:
            discount.payment_id = payment_id


async def get_users_for_winback(
    session: AsyncSession, days_after_expiry: int = 3
) -> List[Subscription]:
    """Find subscriptions that expired approximately `days_after_expiry` days ago,
    where the user does NOT already have an active (unredeemed, non-expired) winback discount."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=days_after_expiry, hours=12)
    window_end = now - timedelta(days=days_after_expiry, hours=-12)

    active_discount_exists = (
        select(WinbackDiscount.discount_id)
        .where(
            WinbackDiscount.user_id == Subscription.user_id,
            WinbackDiscount.redeemed_at.is_(None),
            WinbackDiscount.expires_at > now,
        )
        .correlate(Subscription)
        .exists()
    )

    # Also check no redeemed discount exists (user already used a winback before)
    any_discount_exists = (
        select(WinbackDiscount.discount_id)
        .where(WinbackDiscount.user_id == Subscription.user_id)
        .correlate(Subscription)
        .exists()
    )

    result = await session.execute(
        select(Subscription)
        .options(selectinload(Subscription.user))
        .where(
            Subscription.end_date.between(window_start, window_end),
            Subscription.skip_notifications == False,
            not_(active_discount_exists),
            not_(any_discount_exists),
        )
    )
    return list(result.scalars().all())


async def get_winback_statistics(session: AsyncSession) -> dict:
    """Get winback discount statistics for admin panel."""
    # Total discounts sent
    total_result = await session.execute(
        select(func.count(WinbackDiscount.discount_id))
    )
    total_sent = total_result.scalar() or 0

    # Redeemed (converted)
    redeemed_result = await session.execute(
        select(func.count(WinbackDiscount.discount_id))
        .where(WinbackDiscount.redeemed_at.is_not(None))
    )
    total_redeemed = redeemed_result.scalar() or 0

    # Revenue from winback payments
    revenue_result = await session.execute(
        select(func.coalesce(func.sum(Payment.amount), 0.0))
        .join(WinbackDiscount, WinbackDiscount.payment_id == Payment.payment_id)
        .where(
            WinbackDiscount.redeemed_at.is_not(None),
            Payment.status == "succeeded",
        )
    )
    winback_revenue = float(revenue_result.scalar() or 0.0)

    # Active (pending) discounts
    now = datetime.now(timezone.utc)
    active_result = await session.execute(
        select(func.count(WinbackDiscount.discount_id))
        .where(
            WinbackDiscount.redeemed_at.is_(None),
            WinbackDiscount.expires_at > now,
        )
    )
    active_pending = active_result.scalar() or 0

    # Expired unused
    expired_result = await session.execute(
        select(func.count(WinbackDiscount.discount_id))
        .where(
            WinbackDiscount.redeemed_at.is_(None),
            WinbackDiscount.expires_at <= now,
        )
    )
    expired_unused = expired_result.scalar() or 0

    conversion_rate = (total_redeemed / total_sent * 100) if total_sent > 0 else 0.0

    return {
        "total_sent": total_sent,
        "total_redeemed": total_redeemed,
        "active_pending": active_pending,
        "expired_unused": expired_unused,
        "conversion_rate": conversion_rate,
        "winback_revenue": winback_revenue,
    }
