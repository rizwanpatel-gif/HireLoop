# HireLoop - Enhanced Automated Interview System

![HireLoop Logo](https://placeholder.com/your-logo.png)

HireLoop is a comprehensive automated interview scheduling system that combines AI candidate analysis with Google Calendar integration and automated email notifications.

## ✨ Features

- 🤖 **AI Analysis** - Automated candidate assessment using DeepSeek AI model
- 📅 **Google Calendar Integration** - Automatic interview scheduling and availability checking
- 📧 **Automated Email Notifications** - For both candidates and interviewers
- 🔄 **Complete Automation Workflow** - End-to-end candidate processing
- 💾 **Database Integration** - Track candidate status and interview details

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.8+
- Google Cloud Platform account with Calendar API enabled
- Email account with SMTP access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/HireLoop.git
   cd HireLoop
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment configuration**
   - Copy `.env.example` to `.env`
   - Fill in required credentials

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

### Configuration

#### 1. Google Calendar API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials:
   - Application type: Desktop application
   - Name: HireLoop Calendar
   - Add authorized redirect URIs:
     - `http://localhost:8080/`
     - `urn:ietf:wg:oauth:2.0:oob`

5. Download credentials as JSON and save as `credentials.json` in the backend directory
6. Run OAuth authentication script:
   ```bash
   cd backend
   python fix_oauth_manually.py
   ```
7. Follow browser instructions to authenticate

#### 2. Email Setup

1. For Gmail:
   - Enable "Less secure app access" or
   - Create an App Password (if using 2FA)
   - Add to `.env`:
     ```
     SMTP_SERVER=smtp.gmail.com
     SMTP_PORT=587
     EMAIL_USERNAME=your-email@gmail.com
     EMAIL_PASSWORD=your-app-password
     ```

#### 3. AI Service Setup

1. Get API key from [OpenRouter](https://openrouter.ai/keys)
2. Add to `.env`:
   ```
   OPENROUTER_API_KEY=your-api-key
   ```

## 🚀 Running the System

### Backend

```bash
cd backend
python main_simple.py
```

### Testing

Create a test candidate:
```bash
python test_automation.py
```

Or use the API directly:
```bash
curl -X POST http://localhost:8000/api/candidates/ -H "Content-Type: application/json" -d "{\"name\":\"Test User\",\"email\":\"test@example.com\",\"position\":\"Developer\",\"skills\":\"Python, JavaScript\",\"experience_years\":5,\"education\":\"Computer Science\",\"current_title\":\"Software Developer\",\"resume_text\":\"Experienced developer with strong technical skills\",\"resume_summary\":\"Testing automation\",\"interview_datetime\":\"2025-08-05T15:00:00\"}"
```

## 📋 API Documentation

Access the interactive API docs at: http://localhost:8000/docs

## 📊 System Architecture

```
┌──────────────┐     ┌───────────────┐     ┌─────────────────┐
│ Candidate    │─────▶ AI Analysis   │─────▶ Calendar Check  │
│ Submission   │     │ (DeepSeek)    │     │ (Google API)    │
└──────────────┘     └───────────────┘     └─────────────────┘
                                                  │
┌──────────────┐     ┌───────────────┐            ▼
│ Database     │◀────▶ Email         │◀────┬─────────────────┐
│ Update       │     │ Notifications │     │ Schedule/Find   │
└──────────────┘     └───────────────┘     │ Alternative     │
                                           └─────────────────┘
```

## 📝 License

[MIT License](LICENSE)

## 👨‍💻 Author

Rizwan Patel

## 🙏 Acknowledgments

- DeepSeek for AI analysis capabilities
- Google Calendar API for scheduling integration
