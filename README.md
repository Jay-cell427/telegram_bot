# 🎬 Cinemate Bot - Movie Request System

## 📝 Description
Cinemate Bot is a Telegram bot that allows users to request movies by making payments. The bot handles user requests, payment processing, and movie delivery through a secure and organized system. Admins can manage movie uploads and track user requests.

## ✨ Features
- User-friendly interface with interactive buttons
- Secure payment processing
- Database storage for user information and payment history
- Admin panel for managing movie uploads
- Automatic notifications for users and admins
- Support for both document and text-based movie uploads

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.7+
- PostgreSQL database
- Telegram bot token from [@BotFather](https://t.me/BotFather)
- Payment provider token (if using Telegram Payments)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Jay-cell427/telegram_bot.git
   cd telegram_-bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   TOKEN=your_telegram_bot_token
   ADMIN_ID=your_telegram_user_id
   DATABASE=postgresql://username:password@localhost:5432/dbname
   ```

5. Initialize the database:
   ```bash
   python JoeMovieBot.py
   ```

### Running the Bot
```bash
python JoeMovieBot.py
```

## 🤖 Bot Commands

### User Commands
- `/start` - Start interacting with the bot
- `/help` - Show help message
- `/request` - Request a movie
- `/mystatus` - Check your pending requests
- `/support` - Contact support

### Admin Commands
- `/addmovie` - Add a movie to a payment
- `/stats` - View bot statistics
- `/panel` - Admin control panel

## 📊 Database Structure
The bot uses PostgreSQL with the following tables:

### `users` Table
- Stores user information (ID, username, name, join date)

### `payments` Table
- Tracks payment information with movie file metadata
- Includes payment status and timestamps

## 🔧 Configuration
Modify `config.py` to:
- Add additional environment variables
- Change logging settings
- Adjust database connection parameters

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Support
For issues or feature requests, please open an issue on GitHub.

---

Enjoy using Cinemate Bot! 🍿🎥
