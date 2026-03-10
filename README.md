# ChampUTM - Smart UTM Link Generator

**ChampUTM** is a powerful, user-friendly UTM tracking and analytics platform that helps marketers create, manage, and analyze campaign links with ease.

## Features

### 🔗 Public Link Generator
- Generate UTM-tagged links instantly without signing up
- Clean, intuitive interface
- Recent links saved locally

### 📋 Presets (Account Required)
- Save reusable UTM templates
- Quick-apply presets to any URL
- Team-wide preset sharing (coming soon)

### 📊 Analytics Dashboard (Account Required)
- Track click performance across all your links
- Breakdown by source, medium, campaign
- Visual charts and insights

### 📦 Bulk Generator (Account Required)
- Upload CSV with multiple URLs
- Apply presets or custom UTM parameters
- Download tracked URLs instantly

## Tech Stack

**Frontend:**
- React 18 with TypeScript
- Vite for fast development
- TailwindCSS for styling
- React Query for data fetching
- Recharts for analytics visualizations

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL for data storage
- Redis for caching
- SQLAlchemy ORM
- Alembic for migrations

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Project Structure

```
champutm/
├── frontend/          # React application
│   ├── src/
│   │   ├── api/       # API client functions
│   │   ├── components/# Reusable UI components
│   │   ├── pages/     # Page components
│   │   └── hooks/     # Custom React hooks
│   └── package.json
│
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # API endpoints
│   │   ├── models/    # Database models
│   │   ├── services/  # Business logic
│   │   └── core/      # Config and security
│   └── requirements.txt
│
└── README.md
```

## Environment Variables

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost/champutm
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

## Deployment

**Frontend:** Vercel
**Backend:** Railway with PostgreSQL + Redis add-ons

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or PR.

---

Built with ❤️ by the Champ team
