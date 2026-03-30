import logging
from dataclasses import dataclass
from typing import Callable, List, Set

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection


@dataclass(frozen=True)
class Migration:
    id: str
    description: str
    upgrade: Callable[[Connection], None]


def _ensure_migrations_table(connection: Connection) -> None:
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    )


def _migration_0001_add_channel_subscription_fields(connection: Connection) -> None:
    inspector = inspect(connection)
    columns: Set[str] = {col["name"] for col in inspector.get_columns("users")}
    statements: List[str] = []

    if "channel_subscription_verified" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN channel_subscription_verified BOOLEAN"
        )
    if "channel_subscription_checked_at" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN channel_subscription_checked_at TIMESTAMPTZ"
        )
    if "channel_subscription_verified_for" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN channel_subscription_verified_for BIGINT"
        )

    for stmt in statements:
        connection.execute(text(stmt))


def _migration_0002_add_referral_code(connection: Connection) -> None:
    inspector = inspect(connection)
    columns: Set[str] = {col["name"] for col in inspector.get_columns("users")}

    if "referral_code" not in columns:
        connection.execute(
            text("ALTER TABLE users ADD COLUMN referral_code VARCHAR(16)")
        )

    connection.execute(
        text(
            """
            WITH generated_codes AS (
                SELECT
                    user_id,
                    UPPER(
                        SUBSTRING(
                            md5(
                                user_id::text
                                || clock_timestamp()::text
                                || random()::text
                            )
                            FROM 1 FOR 9
                        )
                    ) AS referral_code
                FROM users
                WHERE referral_code IS NULL OR referral_code = ''
            )
            UPDATE users AS u
            SET referral_code = g.referral_code
            FROM generated_codes AS g
            WHERE u.user_id = g.user_id
            """
        )
    )

    connection.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_users_referral_code
            ON users (referral_code)
            WHERE referral_code IS NOT NULL
            """
        )
    )


def _migration_0003_normalize_referral_codes(connection: Connection) -> None:
    inspector = inspect(connection)
    columns: Set[str] = {col["name"] for col in inspector.get_columns("users")}
    if "referral_code" not in columns:
        return

    connection.execute(
        text(
            """
            UPDATE users
            SET referral_code = UPPER(referral_code)
            WHERE referral_code IS NOT NULL
              AND referral_code <> UPPER(referral_code)
            """
        )
    )


def _migration_0004_add_has_seen_onboarding(connection: Connection) -> None:
    inspector = inspect(connection)
    columns: Set[str] = {col["name"] for col in inspector.get_columns("users")}

    if "has_seen_onboarding" not in columns:
        # Add column with default FALSE
        connection.execute(
            text(
                "ALTER TABLE users ADD COLUMN has_seen_onboarding BOOLEAN NOT NULL DEFAULT FALSE"
            )
        )
        # Set TRUE for all existing users (only new users will see onboarding)
        connection.execute(
            text(
                "UPDATE users SET has_seen_onboarding = TRUE WHERE has_seen_onboarding = FALSE"
            )
        )


def _migration_0005_add_winback_discounts(connection: Connection) -> None:
    inspector = inspect(connection)
    tables = inspector.get_table_names()
    if "winback_discounts" not in tables:
        connection.execute(
            text(
                """
                CREATE TABLE winback_discounts (
                    discount_id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id),
                    discount_percent INTEGER NOT NULL DEFAULT 15,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    expires_at TIMESTAMPTZ NOT NULL,
                    redeemed_at TIMESTAMPTZ,
                    payment_id INTEGER REFERENCES payments(payment_id)
                )
                """
            )
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS ix_winback_discounts_user_id ON winback_discounts (user_id)")
        )


MIGRATIONS: List[Migration] = [
    Migration(
        id="0001_add_channel_subscription_fields",
        description="Add columns to track required channel subscription verification",
        upgrade=_migration_0001_add_channel_subscription_fields,
    ),
    Migration(
        id="0002_add_referral_code",
        description="Store short referral codes for users and backfill existing rows",
        upgrade=_migration_0002_add_referral_code,
    ),
    Migration(
        id="0003_normalize_referral_codes",
        description="Normalize referral codes to uppercase for consistent lookups",
        upgrade=_migration_0003_normalize_referral_codes,
    ),
    Migration(
        id="0004_add_has_seen_onboarding",
        description="Add has_seen_onboarding field for tracking first-time users",
        upgrade=_migration_0004_add_has_seen_onboarding,
    ),
    Migration(
        id="0005_add_winback_discounts",
        description="Add winback_discounts table for post-expiry discount notifications",
        upgrade=_migration_0005_add_winback_discounts,
    ),
]


def run_database_migrations(connection: Connection) -> None:
    """
    Apply pending migrations sequentially. Already applied revisions are skipped.
    """
    _ensure_migrations_table(connection)

    applied_revisions: Set[str] = {
        row[0]
        for row in connection.execute(
            text("SELECT id FROM schema_migrations")
        )
    }

    for migration in MIGRATIONS:
        if migration.id in applied_revisions:
            continue

        logging.info(
            "Migrator: applying %s – %s", migration.id, migration.description
        )
        try:
            with connection.begin_nested():
                migration.upgrade(connection)
                connection.execute(
                    text(
                        "INSERT INTO schema_migrations (id) VALUES (:revision)"
                    ),
                    {"revision": migration.id},
                )
        except Exception as exc:
            logging.error(
                "Migrator: failed to apply %s (%s)",
                migration.id,
                migration.description,
                exc_info=True,
            )
            raise exc
        else:
            logging.info("Migrator: migration %s applied successfully", migration.id)
