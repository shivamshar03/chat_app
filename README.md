# FastAPI + Socket.IO Chat

A minimal, production-ready starting point for a chat app using **FastAPI** and **python-socketio**.

## Features
- Async Socket.IO server mounted into FastAPI (`/socket.io`)
- Rooms (join/leave), usernames, message broadcasting
- Recent message history per room (in-memory buffer)
- REST endpoints: `/health`, `/rooms/{room}/recent`
- Simple web client (Jinja template + vanilla JS + Socket.IO client)
- CORS enabled for local development

## Project structure
```
fastapi-socketio-chat/
├─ app/
│  └─ main.py
├─ templates/
│  └─ index.html
├─ static/
│  └─ style.css
└─ requirements.txt
```

## Run locally

1) Create and activate a virtualenv (recommended)
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

2) Install deps
```bash
pip install -r requirements.txt
```

3) Start the server
```bash
uvicorn app.main:socket_app --reload
```

4) Open the app
- Visit http://127.0.0.1:8000 to use the demo chat UI.
- Socket.IO endpoint is served at `/socket.io`.

## Production notes
- Replace the in-memory `recent_messages` with Redis or a database.
- Put Uvicorn behind a reverse proxy (e.g., Nginx) and enable TLS.
- Scope `CORS` to your actual frontend domains.
- For horizontal scaling, use a message queue or the `socketio.AsyncRedisManager` to share room events across workers.
  ```python
  import socketio
  mgr = socketio.AsyncRedisManager("redis://localhost:6379/0")
  sio = socketio.AsyncServer(async_mode="asgi", client_manager=mgr, cors_allowed_origins="*")
  ```

## API quick test
```bash
# health
curl http://127.0.0.1:8000/health

# recent messages for "general"
curl http://127.0.0.1:8000/rooms/general/recent
```
