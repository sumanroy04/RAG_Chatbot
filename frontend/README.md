# Patronus AI — React Frontend

A React + TypeScript port of the Patronus AI Streamlit UI (`app.py`), built with Vite. It
talks to the existing FastAPI backend defined in `main.py` (`POST /chat`), and reuses the
crisis-response logic from `crisis.py` for display purposes.

## Features ported from the Streamlit app

- Sidebar: brand header, "+ New Chat", recent chats (last 5 user messages), current
  mood/topic focus card, "Export Chat to PDF", and an about card.
- Header with a light/dark mode toggle (same color tokens as the Streamlit theme).
- Hero strip with a live "context pill" showing the selected mood/topic.
- Mood selector (😊 Happy, 😌 Calm, 😐 Okay, 😔 Sad, 😤 Stressed) with an acknowledgement note.
- Topic chips (📚 Study Stress, 😴 Sleep Issues, 💖 Relationships, 😰 Anxiety). Clicking a
  chip sends the same "starter" message the Streamlit app sends, and gets an immediate reply.
- Chat window with user/assistant avatars, markdown-lite rendering (bold + bullet lists),
  and a typing indicator.
- Crisis support card (Tele-MANAS, KIRAN, Vandrevala, iCALL, 112) shown whenever the backend
  flags a message as `is_crisis: true`.
- PDF export of the conversation (via `jspdf`, mirroring `export_chat_pdf()` in `app.py`).

## Getting started

```bash
npm install
cp .env.example .env   # adjust VITE_API_BASE_URL if needed
npm run dev
```

The app runs at `http://localhost:5173` by default and expects the FastAPI backend
(`main.py`) to be running at the URL set in `VITE_API_BASE_URL` (defaults to
`http://localhost:8000`).

## Backend setup (`main.py`)

Run the FastAPI app as usual:

```bash
uvicorn main:app --reload
```

### Enable CORS

`main.py` does not currently configure CORS, so the browser will block requests from the
Vite dev server. Add this near the top of `main.py`, right after `app = FastAPI(...)`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # add your deployed frontend URL too
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Project structure

```
src/
├── api.ts                 # fetch wrapper for POST /chat
├── constants.ts            # mood/topic profiles, starters, acknowledgements (ports main.py)
├── types.ts                 # shared TS types
├── styles/global.css        # design tokens + layout (ports the Streamlit CSS)
├── utils/
│   ├── formatMessage.ts     # plain-text -> simple HTML (ports render_message_text)
│   └── exportPdf.ts          # PDF export (ports export_chat_pdf)
└── components/
    ├── Sidebar.tsx
    ├── Header.tsx
    ├── HeroStrip.tsx
    ├── MoodSelector.tsx
    ├── TopicChips.tsx
    ├── ChatWindow.tsx
    ├── ChatMessage.tsx
    ├── ChatInput.tsx
    └── CrisisCard.tsx        # ports crisis.py's get_crisis_html_card
```

## Notes / things you may want to adjust

- **Conversation memory**: the current `/chat` endpoint in `main.py` builds a brand-new
  `ConversationalRetrievalChain` (with empty memory) on every request, so the backend has no
  multi-turn memory yet — the frontend keeps the full visual transcript, but the model only
  sees the latest message plus retrieved context. If you want real multi-turn memory, the
  backend would need to either persist the chain/memory per session or accept and replay
  prior turns.
- **Hero image**: the Streamlit app embedded a mental-health-awareness banner image behind
  the hero strip. This port keeps the hero strip as a clean glass panel; drop an image into
  `src/assets/` and reference it in `global.css` (`.hero-strip`) if you'd like it back.
- **"Recent chats" buttons**: these are display-only, matching the original Streamlit
  behavior (clicking them didn't do anything there either).
