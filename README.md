# GitHub Documentation for JoeMovieBot

## Overview

JoeMovieBot is a Telegram bot designed to facilitate the purchase and delivery of digital content (primarily cybersecurity-related files) using Telegram's payment system. The bot handles user authentication, payment processing, content requests, and delivery with robust error handling and admin controls.

## Features

### Core Functionality
- **User Management**: Tracks users and their activity
- **Payment Processing**: Handles Telegram payments and records transactions
- **Content Delivery**: Manages content requests and file delivery
- **Admin Controls**: Comprehensive admin panel for managing requests and payments

### Key Components
- **Database**: PostgreSQL backend for storing user, payment, and content information
- **Payment System**: Integration with Telegram's payment API
- **Content Management**: Tools for admins to attach and deliver content files
- **Automated Cleanup**: Background tasks for expired requests and membership checks

## Installation

### Prerequisites
- Python 3.7+
- PostgreSQL database
- Telegram bot token
- Payment provider token

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/JoeMovieBot.git
   cd JoeMovieBot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file based on the following template:
   ```
   # Telegram
   TOKEN=your_telegram_bot_token
   ADMIN_ID=your_admin_user_id
   ADMIN_CHANNEL_ID=your_admin_channel_id
   ADVERTISING_CHANNEL=your_advertising_channel

   # Database
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=your_db_port

   # Payments
   PAYMENT_PROVIDER_TOKEN=your_payment_provider_token
   CURRENCY=XTR
   PRICE_AMOUNT=500

   # System
   REQUEST_EXPIRY_HOURS=24
   MEMBERSHIP_CHECK_INTERVAL=86400
   CLEANUP_INTERVAL=3600
   ```

4. Initialize the database:
   ```bash
   python JoeMovieBot.py
   ```

## Usage

### User Commands
- `/start` - Begin interaction with the bot
- `/help` - Show help message
- `/request` - Request content (also available via button)
- `/mystatus` - Check pending requests
- `/support` - Contact support

### Admin Commands
- `/addcontent` - Add content to a payment
- `/checkpayment` - Check payment details
- `/pending` - List pending payments
- `/stats` - View bot statistics
- `/panel` - Admin control panel
- `/getpayments` - List all payment IDs

## Database Schema

The bot uses the following database tables:

### `users`
- `user_id` (BIGINT) - Primary key
- `username` (VARCHAR(32)) - Telegram username
- `first_name` (VARCHAR(64)) - User's first name
- `last_name` (VARCHAR(64)) - User's last name
- `last_active` (TIMESTAMP) - Last activity timestamp

### `payments`
- `payment_id` (VARCHAR(128)) - Primary key
- `user_id` (BIGINT) - References users(user_id)
- `amount` (INTEGER) - Payment amount
- `currency` (VARCHAR(3)) - Currency code
- `status` (VARCHAR(16)) - Payment status
- `request_timestamp` (TIMESTAMP) - When request was made
- `completion_timestamp` (TIMESTAMP) - When content was delivered
- `expiry_timestamp` (TIMESTAMP) - When request expires
- `file_id` (VARCHAR(128)) - Telegram file ID
- `file_name` (VARCHAR(256)) - Content file name
- `file_type` (VARCHAR(64)) - Content MIME type

### `file_cache`
- `payment_id` (VARCHAR(128)) - Primary key, references payments(payment_id)
- `file_id` (VARCHAR(128)) - Telegram file ID
- `file_name` (VARCHAR(256)) - File name
- `file_type` (VARCHAR(64)) - File MIME type
- `cached_at` (TIMESTAMP) - When file was cached

## Architecture

The bot follows a modular architecture with clear separation of concerns:

1. **Database Layer** (`database.py`):
   - Handles all database operations
   - Manages connections and queries
   - Provides static methods for data access

2. **Configuration** (`config.py`):
   - Centralized configuration management
   - Environment variable validation
   - Constants definition

3. **Bot Logic** (`JoeMovieBot.py`):
   - Telegram bot handlers
   - Payment processing
   - Content delivery workflow
   - Admin functions
   - Background tasks

## Deployment

### Running the Bot
```bash
python JoeMovieBot.py
```

### Systemd Service (for Linux servers)
Create a service file at `/etc/systemd/system/joemoviebot.service`:
```ini
[Unit]
Description=JoeMovieBot Telegram Bot
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/JoeMovieBot
ExecStart=/usr/bin/python3 /path/to/JoeMovieBot/JoeMovieBot.py
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:
```bash
sudo systemctl enable joemoviebot
sudo systemctl start joemoviebot
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact the maintainers directly.
