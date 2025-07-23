**🎬 MovieBot: Telegram Content Delivery Bot**

MovieBot is a Telegram bot designed to manage and deliver exclusive digital content (e.g., cybersecurity resources, movies, documents) to users after a successful payment. It integrates with PostgreSQL for database management, Google Drive for content storage, and a payment provider (like Stripe) for handling transactions.
**✨ Features**

   User Management: Tracks users, their requests, and payment history.

   Content Request System: Users can request content via a simple command or button.

   Payment Integration: Handles invoices, pre-checkout queries, and successful payment callbacks using a Telegram Payment Provider.
 
  Google Drive Integration: Securely delivers content stored in Google Drive to users upon payment completion.

 Admin Panel: Provides administrators with commands to manage content, deliver paid content, view statistics, and manage payments. 
  
  Channel Membership Check: Ensures users are members of a specified Telegram channel before allowing content requests.

   Robust Logging & Error Handling: Comprehensive logging for monitoring and custom error handling for network and Telegram API issues.

   Graceful Shutdown: Handles bot shutdown gracefully to prevent data corruption.

   Periodic Tasks: Automated cleanup of expired pending payments and membership checks.

**🚀 Getting Started**

Follow these steps to set up and run your MovieBot.
Prerequisites

Before you begin, ensure you have the following:

   Python 3.9+: Download Python

   PostgreSQL Database: A running PostgreSQL instance.

   Telegram Bot Token: Obtain this from BotFather on Telegram.

   Telegram Admin ID: Your personal Telegram User ID.

   Telegram Admin Channel ID: The ID of a private channel where the bot sends admin notifications (e.g., -1001234567890).

   Telegram Advertising Channel & Invite Link: A public or private channel users must join.

   Telegram Payment Provider Token: Obtain this from BotFather (e.g., for Stripe, create a test token).

   Google Cloud Project: With Google Drive API enabled.

   Google Service Account Key: A JSON key file for Google Drive API access.

   Google Drive Content Folder ID: The ID of the Google Drive folder where your content files are stored.

Installation

   Clone the repository:

    git clone https://github.com/your-username/MovieBot.git
    cd MovieBot

   Create a virtual environment and activate it:

    python3 -m venv botenv
    source botenv/bin/activate

   Install dependencies:

    pip install -r requirements.txt

   (Make sure you have a requirements.txt file with python-telegram-bot, psycopg2-binary, aiopg, python-dotenv, google-api-python-client, google-auth-httplib2, google-auth-oauthlib, aiohttp).

Configuration (.env file)

Create a .env file in the root directory of your project and populate it with your credentials and settings.

    # Telegram Bot Token (from BotFather)
    TOKEN="YOUR_TELEGRAM_BOT_TOKEN"

    # Admin User ID (your Telegram user ID)
    ADMIN_ID=1234567890

    # Admin Channel ID (where bot sends notifications, e.g., -1001234567890)
    ADMIN_CHANNEL_ID="-100XXXXXXXXXXXXX"

    # Advertising Channel Username (e.g., @YourChannel)
    ADVERTISING_CHANNEL="@YourAdvertisingChannel"

    # Advertising Channel Invite Link (e.g., https://t.me/joinchat/ABCDEF12345)
    ADVERTISING_CHANNEL_INVITE_LINK="https://t.me/joinchat/YOUR_INVITE_LINK"

    # Advertising Channel Numerical ID (e.g., -1001234567890)
    ADVERTISING_CHANNEL_ID="-100XXXXXXXXXXXXX"

    # Database Credentials (PostgreSQL)
    DB_NAME="your_db_name"
    DB_USER="your_db_user"
    DB_PASSWORD="your_db_password"
    DB_HOST="localhost"
    DB_PORT="5432"

    # Payment Provider Token (from BotFather, e.g., Stripe test token)
    PAYMENT_PROVIDER_TOKEN="YOUR_PAYMENT_PROVIDER_TOKEN"

    # Currency for payments (e.g., USD, EUR, XTR)
    CURRENCY="XTR"

    # Price amount in smallest units (e.g., 500 for $5.00, 1 for 1 XTR)
    PRICE_AMOUNT=1

    # System Settings
    REQUEST_EXPIRY_HOURS=24
    MEMBERSHIP_CHECK_INTERVAL=86400 # Seconds (24 hours)
    CLEANUP_INTERVAL=3600 # Seconds (1 hour)

    # Google Drive API Credentials
    # Path to your service account JSON key file
    GOOGLE_DRIVE_CREDENTIALS_PATH="./path/to/your/service_account_key.json"

    # Google Drive Folder ID where your content is stored
    GOOGLE_DRIVE_CONTENT_FOLDER_ID="YOUR_GOOGLE_DRIVE_FOLDER_ID"

    Database Setup

The bot uses PostgreSQL. You need to initialize the database schema. The database.py file contains the necessary functions.

Run the bot once, and it will attempt to initialize the database tables if they don't exist. Ensure your PostgreSQL server is running and accessible with the credentials provided in .env.

**Google Drive API Setup**

   Enable Google Drive API: Go to the Google Cloud Console, select your project, and enable the "Google Drive API" under "APIs & Services" > "Library".

   Create Service Account:

   In the Google Cloud Console, navigate to "IAM & Admin" > "Service Accounts".

   Click "CREATE SERVICE ACCOUNT".

   Give it a name and description.

   Grant it the "Google Drive API Editor" role (or a more restricted role if you know exactly what permissions are needed, but Editor is usually sufficient for reading/downloading).

   Create Key: After creating the service account, click on it, go to the "Keys" tab, and click "ADD KEY" > "Create new key" > "JSON". This will download your service account JSON key file.

  Place Key File: Save this JSON key file to the path specified in GOOGLE_DRIVE_CREDENTIALS_PATH in your .env file (e.g., ./service_account_key.json).

   Share Google Drive Folder: Share the Google Drive folder (specified by GOOGLE_DRIVE_CONTENT_FOLDER_ID) with the email address of your newly created service account. The email address will look something like your-service-account-name@your-project-id.iam.gserviceaccount.com.

Running the Bot

Once all configurations are set, you can run the bot:

    python JoeMovieBot.py

The bot will perform network connectivity tests, initialize components, and then start polling for updates.

**🤖 Bot Commands**

User Commands

    /start: 
    
   Initiates interaction with the bot and displays a welcome message with main options.

    /request:
    
   Guides the user through the content request and payment process.

    /mystatus: 
    
   Shows the user's last few content requests and their status.

    /help: 
    
   Displays a list of all available bot commands and their descriptions.

    /support: 
    
   Provides information on how to contact support.

Admin Commands (Requires ADMIN_ID in .env)

    /admin: 
    
   Checks if the user is recognized as an administrator.

    /panel: 
    
   Displays an inline keyboard with quick access to other admin commands.

    /addcontent <content_title> <google_drive_file_id> [file_type]:
    
   Registers new content in the bot's CMS library.

        content_title: The title of the content (e.g., "Advanced Phishing Techniques").

        google_drive_file_id: The Google Drive ID of the file.

        file_type (optional): video or document. Defaults to document.

    /deliver <payment_id> <content_id>: 
    
   Delivers content to a user after a successful payment.

        payment_id: The unique ID of the completed payment.

        content_id: The ID of the content from the CMS library (obtained via /addcontent).

    /checkpayment [payment_id]:
   
   Checks the details of a specific payment. If payment_id is omitted, the bot will prompt for it.

    /pending: 
    
   Lists all pending payments that require content delivery.

    /getpayments: 
    
   Lists all payment IDs with their current statuses.

    /stats: 
    
   Displays overall bot statistics (total users, payments, revenue, etc.).

**💳 Payment Flow**

   User Requests Content: The user initiates a content request via /request or the "Request Content" button.

   Channel Check: The bot verifies if the user is a member of the required advertising channel.

   Invoice Generation: If eligible, the bot presents a "Proceed to Payment" button. Clicking this generates a Telegram invoice.

   Pending Payment Record: A record for the pending payment is created in the database.

   Pre-Checkout Query: When the user attempts to pay, Telegram sends a PreCheckoutQuery. The bot verifies the payment ID against its pending records.

   Successful Payment Callback: Upon successful payment, Telegram sends a SuccessfulPayment update. The bot updates the payment status in the database to 'completed' and notifies the admin.

  Admin Delivery: An administrator uses the /deliver command with the payment ID and content ID to send the content to the user.

**🗃️ Content Management**

Content files are stored in Google Drive. The bot does not store the files directly but rather their Google Drive IDs and metadata in its PostgreSQL database.

   Adding Content: Admins use /addcontent to register content. This command takes a title, the Google Drive File ID, and an optional file type.

   Delivering Content: Once a payment is complete, an admin uses /deliver to link the payment to a specific content ID and trigger the content download from Google Drive and delivery to the user.

**🛠️ Error Handling and Logging**

The bot implements robust error handling for network issues, Telegram API errors, and database operations. All significant events and errors are logged to the console, providing clear insights into the bot's operation and potential problems. Critical errors also trigger notifications to the ADMIN_ID.
🤝 Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

   Fork the repository.

   Create a new branch (git checkout -b feature/your-feature-name).

   Make your changes.

   Commit your changes (git commit -m 'Add new feature').

   Push to the branch (git push origin feature/your-feature-name).

   Create a Pull Request.

**📄 License**

This project is licensed under the MIT License - see the LICENSE file for details.
