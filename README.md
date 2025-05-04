# CineMate Bot 🎥🤖

A Telegram bot for managing and delivering movie requests with file upload support.

## Features ✨

- **User-friendly interface** with `/start` command and interactive buttons
- **Admin panel** for managing movie deliveries
- **File upload support** for videos, documents, photos, and audio
- **Database integration** with PostgreSQL for tracking users and payments
- **Admin commands** for managing content delivery
- **Automatic restart** on crashes for maximum uptime

## Commands 🛠️

### User Commands
-`/start` - Start interacting with the bot
- `/help` - Show help message
- `/support` - Contact support

### Admin Commands
- `/addmovie <payment_id> <file_id> "<file_name>" <file_type>` - Add a movie file to a payment
- `/panel` - Admin control panel
- `/checkfiles` - View file delivery status
- `/getpayments` - View recent payments
- `/admin` - Verify admin status

## Database Schema 🗃️

The bot uses PostgreSQL with these tables:

### `users` table
- `user_id` (BIGINT PRIMARY KEY)
- `username` (TEXT)
- `first_name` (TEXT)
- `last_name` (TEXT)
- `join_date` (TIMESTAMP)
- `last_active` (TIMESTAMP)

### `payments` table
- `payment_id` (TEXT PRIMARY KEY)
- `user_id` (BIGINT REFERENCES users)
- `amount` (INTEGER)
- `currency` (TEXT)
- `status` (TEXT)
- `request_timestamp` (TIMESTAMP)
- `completion_timestamp` (TIMESTAMP)
- `file_id` (TEXT)
- `file_name` (TEXT)
- `file_type` (TEXT)

## Setup Instructions ⚙️

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cinemate-bot.git
   cd cinemate-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file with:
   ```
   TOKEN=your_telegram_bot_token
   DATABASE=your_postgres_connection_string
   ```

4. **Run the bot**
   ```bash
   python JoeMovieBotFree.py
   ```

## Configuration ⚙️

Edit `config.py` to set:
- `ADMIN_ID` - Your Telegram user ID
- Environment variables in `.env` file:
  - `TOKEN` - Your Telegram bot token
  - `DATABASE` - PostgreSQL connection string

## Requirements 📦

- Python 3.7+
- `python-dotenv`
- `psycopg2-binary`
- `pyTelegramBotAPI`

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Enjoy using Cinemate Bot! For support, contact the developer. 🚀
