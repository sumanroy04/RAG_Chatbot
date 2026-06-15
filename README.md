# 🛡️ Patronus AI: RAG Mental Health Chatbot

> A secure, empathetic, and context-grounded conversational companion for mental health support, built with Retrieval-Augmented Generation (RAG).

[![React](https://img.shields.io/badge/React-18.x-61DAFB?logo=react&logoColor=black&style=flat-square)](#)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white&style=flat-square)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.x-009688?logo=fastapi&logoColor=white&style=flat-square)](#)
[![LangChain](https://img.shields.io/badge/LangChain-0.2.x-1C3C3A?logo=chainlink&logoColor=white&style=flat-square)](#)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorStore-orange?style=flat-square)](#)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white&style=flat-square)](#)

---

## 🎨 User Interface Preview

Here is a glimpse of the application's clean design system and user workflows:

### 1. Interactive RAG Chat Interface
A responsive real-time conversational chat pane styled with curated dark modes, custom typography, and dynamic transitions.
![Chat Screen 1](D:\Projects Foder\RAG_Chatbot\data-storage\images\screen_shot_1.png.png)

### 2. Crisis & Safety Card Trigger
When self-harm or emergency triggers are detected, the system immediately bypasses LLM generations to deliver verified local emergency resources.
![Crisis Screen 2](D:\Projects Foder\RAG_Chatbot\data-storage\images\screen_shot_2.png)

### 3. Therapist Scheduling Grid
A grid-based appointment scheduler that allows users to book and cancel consulting sessions.
![Scheduler Screen 3](D:\Projects Foder\RAG_Chatbot\data-storage\images\screen_shot_3.png)

---

## ✨ Key Features

*   **Retrieval-Augmented Generation (RAG)**: Uses semantic matching from local ChromaDB directories containing trusted medical literature (WHO and Ministry of Health guidelines) to prevent hallucinated advice.
*   **Emergency Safety Shield**: Parses user inputs using a pattern-matching filter. Distressing terms automatically trigger a crisis helpline overlay.
*   **Crisis Incident Logger**: Persists and flags user messages containing harmful keywords (along with user association, matched terms, and timestamp) in a dedicated relational database table (`crisis_logs`) for professional review.
*   **Therapist Scheduling System**: Booking slot manager integrated with mock email and SMS delivery confirmations.
*   **Static Resource Library**: In-app educational guidelines filtered by categories (e.g. Anxiety, Stress, Depression) and searchable tags.
*   **Cross-Site Scripting (XSS) Sanitizer**: Automatically cleans and pre-escapes bot/user markdown messages prior to injection.
*   **JWT User Authentication**: Encrypted user registration and sign-in pipelines powered by bcrypt hashes.

---

## 🛠️ Installation & Setup Guide

### 📋 Prerequisites
*   **Python**: 3.13 or 3.14
*   **Node.js**: v18+ & NPM

### 1. Clone & Set Environment Variables
Create a file named `.env` in the root folder:
```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///backend/mental_health.db
JWT_SECRET_KEY=use_a_strong_random_secret_here
```

### 2. Running via Automatic Script
We have included a PowerShell script `run.ps1` that automatically activates the environment, installs both frontend and backend requirements, and launches both local servers:
```powershell
./run.ps1
```

### 3. Running Manually
If you prefer running the servers in independent terminals:

#### Terminal 1: FastAPI Backend
```bash
# Initialize virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install requirements & run
pip install -r requirements/base.txt
python -m uvicorn backend.main:app --port 8000 --reload
```

#### Terminal 2: React Vite Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📁 Repository Map

```
RAG_Chatbot/
├── backend/                      # Python FastAPI Backend API
│   ├── app/                      # CORS, extensions, config loader, error handlers
│   ├── auth/                     # JWT Authentication routes & models
│   ├── api/                      # Appointments, resources, chat, and crisis routes/models
│   ├── chatbot/                  # ChromaDB loader, input parser, RAG & LLM response logic
│   ├── services/                 # Email, SMS, and calendar mock integration stubs
│   ├── tasks/                    # Scheduled reminder triggers
│   └── main.py                   # API entry point wrapper
│
├── frontend/                     # React Vite Single Page App (TypeScript)
│   ├── src/
│   │   ├── components/           # UI Component blocks (chat, common, auth, appointments)
│   │   ├── services/             # Axios connection middlewares
│   │   └── App.tsx               # Main Dashboard Router and State manager
│   └── package.json              # NPM Package descriptors
│
├── data-storage/                 # Vector db state and resource attachments
│   ├── data/                     # Raw PDFs used to train/ground the database
│   └── images/                   # UI Assets and screenshot documentation
└── requirements/                 # Dependency requirement files
```

---

## 🔌 REST API Documentation

FastAPI exposes endpoints structured into four main route domains:

### 1. Authentication (`/api/auth`)
*   `POST /api/auth/register`: Register a user.
*   `POST /api/auth/login`: Authenticate credentials. Returns standard bearer JWT token.
*   `GET /api/auth/me`: Verifies user session.

### 2. Appointments (`/api/appointments`)
*   `GET /api/appointments`: Fetches user's appointments.
*   `POST /api/appointments`: Book a new session slot.
*   `DELETE /api/appointments/{id}`: Cancel a session.

### 3. Resources Library (`/api/resources`)
*   `GET /api/resources`: Fetch self-help articles filtered by tags or categories.

### 4. Chat (`/chat`)
*   `POST /chat`: Interact with RAG chatbot. Saves history (mapped to `user_id` if authenticated).

### 5. Crisis Logging (`/api/crisis`)
*   `GET /api/crisis/logs`: Retrieve flagged crisis incidents. **Admins and therapists can see all crisis logs**; regular users can retrieve only their own flagged events.

---

## 📖 Extended Documentation Index
*   🎓 **[Academic Project Documentation](file:///d:/Projects%20Foder/RAG_Chatbot/docs/project_documentation.md)**: Final Year Project report containing system feasibility study, DFD matrices, UML diagrams, QA test case worksheets, and reference bibliographies.
*   🛠️ **[Developer Architecture Guidelines](file:///d:/Projects%20Foder/RAG_Chatbot/docs/detailed_system_documentation.md)**: Full database table schemas, FastAPI route details, parameters validation checklists, security checks, and code configurations.
