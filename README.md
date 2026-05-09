# Gold & Silver Price Tracker 🚀💰

A professional, institutional-grade real-time market surveillance platform for tracking Gold and Silver prices with automated multi-channel alerts.

## 🌟 Features

- **Real-Time Monitoring:** Live price tracking of Gold (XAU/USD) and Silver (XAG/USD) via high-performance TradingView charts.
- **Automated Alerts:** Set custom percentage-based thresholds (e.g., "Notify me if Gold increases by 2%") and receive instant notifications.
- **Multi-Channel Notifications:**
  - **Email:** Automated professional alerts sent directly to your Gmail.
  - **Telegram:** Instant messages via a custom bot linked to your account.
- **AI Predictions:** 24-hour market trend forecasting.
- **Premium UI:** Sleek, dark-mode dashboard with glassmorphism aesthetics and responsive design.
- **PDF Reporting:** Download detailed market surveillance reports for Gold and Silver.

## 🛠️ Technology Stack

- **Backend:** Django 4.2 (Python)
- **Database:** SQLite (Development) / PostgreSQL (Production ready)
- **Task Scheduling:** APScheduler for real-time price checking.
- **Styling:** Vanilla CSS3 + Bootstrap 5 (Modern aesthetics).
- **APIs:** Integrated with GoldAPI.io and TradingView.

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tharunkumar-p-css/gold_sliver_traker.git
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file based on `.env.example` and add your:
   - `EMAIL_HOST_USER` & `EMAIL_HOST_PASSWORD` (Gmail App Password)
   - `TELEGRAM_BOT_TOKEN`
   - `GOLDAPI_KEY`

4. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start the Server:**
   ```bash
   python manage.py runserver
   ```

## 🔒 Security Note
The `.env` file and `db.sqlite3` are automatically ignored by Git to ensure your private keys and user data never leave your local environment.

---
Built with ❤️ for advanced market surveillance.
