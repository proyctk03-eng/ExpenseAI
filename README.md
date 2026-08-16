# 💰 ExpenseAI

## Smart Personal Finance Management with AI Integration

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![AI Powered](https://img.shields.io/badge/AI-Powered-FF6B6B.svg)]()

> 🚀 **ExpenseAI** - Automate your personal finance tracking with the power of AI.  
> Let AI classify your transactions and provide personalized financial advice.

---

## 📸 Screenshots & Demo

*(Vui lòng thay thế các link ảnh dưới đây bằng ảnh thực tế của bạn)*

![Dashboard](https://via.placeholder.com/800x400.png?text=ExpenseAI+Dashboard)
*Real-time dashboard with income, expenses, and AI-powered advice.*

![Transactions](https://via.placeholder.com/800x400.png?text=Transaction+Management)
*Manage your daily transactions effortlessly.*

---

## ✨ Features

### Core Features
- ✅ **Smart Transaction Management** - Add, edit, delete transactions with ease
- ✅ **AI-Powered Classification** - Auto-categorize transactions using OpenAI API
- ✅ **Personalized AI Advice** - Get financial tips based on your spending patterns
- ✅ **Visual Analytics** - Beautiful charts and graphs (Pie, Bar, Trend)
- ✅ **Real-time Dashboard** - View your income, expenses, and balance at a glance

### Security & Privacy
- 🔐 **JWT Authentication** - Secure login with HttpOnly Cookies & refresh tokens
- 🛡️ **Rate Limiting** - Protection against brute-force attacks via SlowAPI
- 🔒 **Password Hashing** - Using bcrypt for secure password storage
- 🚫 **SQL Injection Prevention** - Using SQLAlchemy ORM with parameterized queries

### Developer Friendly
- 🐳 **Docker Ready** - One-command deployment
- 📦 **Well-structured** - Clean architecture with MVC pattern
- 🧪 **Tested** - Comprehensive unit and integration tests
- 📚 **Full API Documentation** - Auto-generated OpenAPI/Swagger docs

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Backend | FastAPI | 0.104+ |
| Database | PostgreSQL | 15+ |
| ORM | SQLAlchemy | 2.0+ |
| Migration | Alembic | 1.13+ |
| AI Integration | OpenAI API (GPT-4o-mini)| - |
| Frontend | HTML + CSS + JS (Vanilla)| - |
| UI Framework | Bootstrap 5 | 5.3+ |
| Container | Docker + Docker Compose | - |
| Testing | Pytest | 7.0+ |

---

## 🚀 Getting Started

### Method 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/[YOUR_USERNAME]/ExpenseAI.git
cd ExpenseAI

# Copy environment variables
cp .env.example .env
# Edit .env with your OpenAI API key
# nano .env

# Build and run with Docker Compose
docker-compose up --build -d

# Run database migrations
docker-compose exec web alembic upgrade head
```
Access the application:
- **Frontend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Method 2: Manual Setup (For Development)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up PostgreSQL Database and update .env with DATABASE_URL

# 4. Run migrations
alembic upgrade head

# 5. Run the application
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📁 Project Structure

```text
expenseai/
├── alembic/                # Database migrations
├── docs/                   # Documentation & Thesis Reports
├── src/                    # Main Source Code
│   ├── api/                # FastAPI Routers
│   ├── middleware/         # Custom Middlewares
│   ├── models/             # SQLAlchemy ORM Models
│   ├── schemas/            # Pydantic Schemas
│   ├── services/           # AI Business Logic
│   ├── static/             # CSS/JS Assets
│   ├── templates/          # HTML Jinja2 Templates
│   └── utils/              # Security, Configs
├── tests/                  # Pytest Unit Tests
├── docker-compose.yml
└── Dockerfile
```

---

## 📚 API Documentation

After running the application, access the auto-generated Swagger UI at:
[http://localhost:8000/docs](http://localhost:8000/docs)

### Key Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login and get HttpOnly JWT token |
| `POST` | `/api/auth/refresh` | Refresh access token |

#### Transactions & Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/transactions/` | Get all transactions |
| `POST` | `/api/transactions/` | Create transaction (Triggers AI) |
| `GET`  | `/api/reports/summary` | Get income/expense summary |
| `POST` | `/api/advice/` | Get AI financial advice |

---

## 🤝 Contributing
We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**⭐ Star this repository if you find it useful!**  
**📧 Contact:** [Your Email/Portfolio Link]
