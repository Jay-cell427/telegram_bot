import aiopg
from aiopg import create_pool
from config import Config
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Database:
    pool = None # Class variable to hold the connection pool

    @staticmethod
    async def get_connection():
        """Creates and returns the database connection pool."""
        if Database.pool is None:
            Database.pool = await create_pool(Config.DATABASE)
        return Database.pool

    @staticmethod
    async def init_db():
        """Initialize database with all required tables and extensions."""
        commands = (
            # Enable uuid-ossp extension
            "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(32),
                first_name VARCHAR(64),
                last_name VARCHAR(64),
                last_active TIMESTAMP DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS payments (
                payment_id VARCHAR(128) PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                amount INTEGER NOT NULL,
                currency VARCHAR(3) NOT NULL,
                status VARCHAR(16) DEFAULT 'pending',
                request_timestamp TIMESTAMP DEFAULT NOW(),
                completion_timestamp TIMESTAMP,
                expiry_timestamp TIMESTAMP GENERATED ALWAYS AS 
                    (request_timestamp + INTERVAL '%s HOURS') STORED,
                content_id UUID -- Changed from file_id, file_name, file_type
            )
            """ % Config.REQUEST_EXPIRY_HOURS,
            """
            -- Create content_library table
            CREATE TABLE IF NOT EXISTS content_library (
                content_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                title VARCHAR(255) NOT NULL UNIQUE,
                file_path TEXT NOT NULL, -- This will store Google Drive File ID or CMS URL
                file_type VARCHAR(50) DEFAULT 'document',
                uploaded_at TIMESTAMP DEFAULT NOW(),
                admin_id BIGINT
            )
            """,
            """
            -- Add foreign key constraint to payments table (if not already added)
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'fk_content'
                ) THEN
                    ALTER TABLE payments
                    ADD CONSTRAINT fk_content
                    FOREIGN KEY (content_id) REFERENCES content_library(content_id)
                    ON DELETE SET NULL;
                END IF;
            END
            $$;
            """
        )
        for command in commands:
            logger.info(f"Executing DB command: {command.splitlines()[0]}...") # Log only first line of command
            await Database.execute_query(command)
        logger.info("Database initialized with tables.")

    @staticmethod
    async def execute_query(query, params=None, fetch=False):
        """
        Executes a database query.
        Relies on aiopg's context manager for transaction handling.
        """
        async with Database.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                if fetch:
                    return await cur.fetchall()
                # Removed explicit await conn.commit()
                # aiopg's 'async with conn:' context manager handles commit/rollback automatically.


    @staticmethod
    async def add_or_update_user(user_id: int, username: str, first_name: str, last_name: str):
        query = """
        INSERT INTO users (user_id, username, first_name, last_name, last_active)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (user_id) DO UPDATE
        SET username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            last_active = NOW();
        """
        await Database.execute_query(query, (user_id, username, first_name, last_name))

    @staticmethod
    async def add_pending_payment(payment_id: str, user_id: int, amount: int, currency: str):
        query = """
        INSERT INTO payments (payment_id, user_id, amount, currency, status)
        VALUES (%s, %s, %s, %s, 'pending');
        """
        await Database.execute_query(query, (payment_id, user_id, amount, currency))

    @staticmethod
    async def update_payment_status(payment_id: str, status: str, provider_charge_id: str = None):
        query = """
        UPDATE payments
        SET status = %s,
            completion_timestamp = NOW(),
            provider_charge_id = %s -- Assuming you added this column for charge ID
        WHERE payment_id = %s;
        """
        await Database.execute_query(query, (status, provider_charge_id, payment_id))

    @staticmethod
    async def get_payment_details(payment_id: str):
        query = """
        SELECT payment_id, user_id, amount, currency, status, content_id
        FROM payments
        WHERE payment_id = %s;
        """
        result = await Database.execute_query(query, (payment_id,), fetch=True)
        if result:
            # Map the result to a dictionary for easier access
            # This assumes a specific order of columns in your SELECT statement
            # Consider fetching column names from cur.description if you want a more robust mapping
            columns = ['payment_id', 'user_id', 'amount', 'currency', 'status', 'content_id']
            return dict(zip(columns, result[0]))
        return None

    @staticmethod
    async def cleanup_expired_pending_payments():
        query = """
        UPDATE payments
        SET status = 'expired'
        WHERE status = 'pending' AND NOW() > expiry_timestamp;
        """
        await Database.execute_query(query)

    @staticmethod
    async def is_user_member(user_id: int):
        # This function might become redundant if membership is checked via Telegram API only
        # or if you track memberships in your DB
        # For now, it's a placeholder.
        return True # Placeholder

    # --- CMS Library Database Methods ---

    @staticmethod
    async def add_content_to_cms_library(content_id: str, title: str, file_path: str, file_type: str):
        """
        Adds new content metadata to the content_library table.
        file_path will store the Google Drive File ID.
        """
        query = """
        INSERT INTO content_library (content_id, title, file_path, file_type)
        VALUES (%s, %s, %s, %s);
        """
        await Database.execute_query(query, (content_id, title, file_path, file_type))

    @staticmethod
    async def get_content_from_cms_library(content_id: str):
        """
        Retrieves content details from the content_library based on content_id.
        """
        query = """
        SELECT content_id, title, file_path, file_type, uploaded_at, admin_id
        FROM content_library
        WHERE content_id = %s;
        """
        result = await Database.execute_query(query, (content_id,), fetch=True)
        if result:
            columns = ['content_id', 'title', 'file_path', 'file_type', 'uploaded_at', 'admin_id']
            return dict(zip(columns, result[0]))
        return None

    @staticmethod
    async def link_content_to_payment(payment_id: str, content_id: str):
        """
        Updates a payment record to link it to a specific content_id.
        """
        query = """
        UPDATE payments
        SET content_id = %s,
            status = 'delivered' -- Optional: Change status to 'delivered' upon linking
        WHERE payment_id = %s;
        """
        await Database.execute_query(query, (content_id, payment_id))


    @staticmethod
    async def get_stats():
        """Returns statistics about users and payments"""
        query = """
        SELECT
            COUNT(DISTINCT p.user_id) AS total_users,
            COUNT(DISTINCT CASE WHEN u.last_active > NOW() - INTERVAL '30 days' THEN p.user_id END) AS active_users,
            COUNT(*) AS total_payments,
            COUNT(CASE WHEN p.status = 'pending' THEN 1 END) AS pending_payments,
            SUM(CASE WHEN p.status = 'completed' THEN amount ELSE 0 END) AS revenue_completed,
            SUM(CASE WHEN p.status = 'pending' THEN amount ELSE 0 END) AS revenue_pending
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.user_id;
        """
        result = await Database.execute_query(query, fetch=True)
        if result:
            # Note: Ensure the column names here match the aliases in the SQL query
            columns = [
                'total_users', 'active_users', 'total_payments',
                'pending_payments', 'revenue_completed', 'revenue_pending'
            ]
            return dict(zip(columns, result[0]))
        return None
