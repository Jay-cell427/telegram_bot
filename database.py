import psycopg2
from config import DATABASE
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with required tables for movie requests"""
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cursor:
            # Create users table if doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP
                )
            ''')

            # Create payments table with enhanced movie file metadata
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id TEXT PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    amount INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completion_timestamp TIMESTAMP,
                    file_id TEXT,
                    file_name TEXT,
                    file_type TEXT,
                    CONSTRAINT unique_user_payment UNIQUE(user_id, payment_id)
                )
            ''')

            # Create index for faster user based queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_payments_user_id 
                ON payments(user_id)
            ''')
            conn.commit()
            logger.info("Database tables initialized/verified")

def add_or_update_user(user_id, username=None, first_name=None, last_name=None):
    """Add new user or update existing user information"""
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET 
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    last_active = CURRENT_TIMESTAMP
            ''', (user_id, username, first_name, last_name))
            conn.commit()
            logger.info(f"Updated user info for {user_id}")

def save_payment(user_id, payment_id, amount, currency, file_id=None, file_name=None, file_type=None):
    """Save payment information to the database with file metadata"""
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO payments (
                    user_id, 
                    payment_id, 
                    amount, 
                    currency,
                    file_id,
                    file_name,
                    file_type
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, payment_id) DO UPDATE
                SET 
                    amount = EXCLUDED.amount,
                    currency = EXCLUDED.currency,
                    file_id = EXCLUDED.file_id,
                    file_name = EXCLUDED.file_name,
                    file_type = EXCLUDED.file_type
            ''', (user_id, payment_id, amount, currency, file_id, file_name, file_type))
            conn.commit()
            logger.info(f"Saved payment {payment_id} for user {user_id}")

def get_user_payments(user_id):
    """Get all payment records for a specific user with file metadata"""
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    payment_id, 
                    amount, 
                    currency, 
                    status, 
                    request_timestamp,
                    file_id,
                    file_name,
                    file_type
                FROM payments
                WHERE user_id = %s
                ORDER BY request_timestamp DESC
            ''', (user_id,))
            return cursor.fetchall()

def get_movie_file_info(user_id, payment_id=None):
    """
    Retrieve movie file metadata for a user
    Returns tuple of (file_id, file_name, file_type) or None
    """
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cursor:
            if payment_id:
                cursor.execute('''
                    SELECT file_id, file_name, file_type FROM payments 
                    WHERE user_id = %s AND payment_id = %s
                ''', (user_id, payment_id))
            else:
                cursor.execute('''
                    SELECT file_id, file_name, file_type FROM payments 
                    WHERE user_id = %s 
                    ORDER BY request_timestamp DESC 
                    LIMIT 1
                ''', (user_id,))
            
            result = cursor.fetchone()
            if result:
                logger.info(f"Retrieved file info for user {user_id}")
                return result
            logger.warning(f"No file info found for user {user_id}")
            return None

def update_movie_file(payment_id, file_id, file_name, file_type):
    """Update payment record and return user_id for notification"""
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cursor:
            # First get user_id associated with this payment
            cursor.execute('''
                SELECT user_id FROM payments WHERE payment_id = %s
            ''', (payment_id,))
            user_id = cursor.fetchone()[0]
            
            # Then update the file info
            cursor.execute('''
                UPDATE payments 
                SET file_id = %s, file_name = %s, file_type = %s,
                    completion_timestamp = CURRENT_TIMESTAMP,
                    status = 'completed'
                WHERE payment_id = %s
            ''', (file_id, file_name, file_type, payment_id))
            conn.commit()
            return user_id  # Return user_id for notification

def update_payment_status(payment_id, status):
    """Update the status of a payment"""
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                UPDATE payments 
                SET status = %s
                WHERE payment_id = %s
            ''', (status, payment_id))
            conn.commit()
            logger.info(f"Updated status for payment {payment_id} to {status}")

def get_user_info(user_id):
    """Retrieve basic user information"""
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    user_id, 
                    username, 
                    first_name, 
                    last_name, 
                    join_date
                FROM users
                WHERE user_id = %s
            ''', (user_id,))
            return cursor.fetchone()