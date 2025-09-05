# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio

# Initialize Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI()
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
# Store messages in memory
rooms_messages = {}
# Serve templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ------------- Chat Events -------------

@sio.event
async def connect(sid, environ):
    print(f"🔌 Client connected: {sid}")
    await sio.emit("server_message", {"sid": sid, "message": "Welcome!"}, to=sid)

@sio.event
async def disconnect(sid):
    print(f"❌ Client disconnected: {sid}")

@sio.event
async def set_username(sid, data):
    username = data.get("username", "guest")
    sio.save_session(sid, {"username": username})
    await sio.emit("username_set", {"sid": sid, "username": username}, to=sid)

@sio.event
async def join_room(sid, data):
    room = data.get("room", "general")
    session = await sio.get_session(sid)
    username = session.get("username", "guest")

    await sio.enter_room(sid, room)
    await sio.emit("user_joined", {"sid": sid, "username": username, "room": room}, room=room)

    # Send recent messages
    recent = rooms_messages.get(room, [])
    await sio.emit("recent_messages", {"room": room, "messages": recent}, to=sid)

@sio.event
async def leave_room(sid, data):
    room = data.get("room", "general")
    session = await sio.get_session(sid)
    username = session.get("username", "guest")

    await sio.leave_room(sid, room)
    await sio.emit("user_left", {"sid": sid, "username": username, "room": room}, room=room)

@sio.event
async def send_message(sid, data):
    room = data.get("room", "general")
    message = data.get("message", "")
    session = await sio.get_session(sid)
    username = session.get("username", "guest")

    entry = {"username": username, "message": message}
    rooms_messages.setdefault(room, []).append(entry)
    if len(rooms_messages[room]) > 50:
        rooms_messages[room] = rooms_messages[room][-50:]  # Keep last 50

    await sio.emit("new_message", {"sid": sid, "username": username, "room": room, "message": message}, room=room)


# ------------- Video Signaling Events -------------

@sio.event
async def offer(sid, data):
    room = data.get("room")
    offer = data.get("offer")
    print(f"📡 Offer from {sid} in {room}")
    await sio.emit("offer", {"sid": sid, "offer": offer}, room=room, skip_sid=sid)

@sio.event
async def answer(sid, data):
    room = data.get("room")
    answer = data.get("answer")
    print(f"📡 Answer from {sid} in {room}")
    await sio.emit("answer", {"sid": sid, "answer": answer}, room=room, skip_sid=sid)

@sio.event
async def ice_candidate(sid, data):
    room = data.get("room")
    candidate = data.get("candidate")
    print(f"📡 ICE candidate from {sid} in {room}")
    await sio.emit("ice_candidate", {"sid": sid, "candidate": candidate}, room=room, skip_sid=sid)


# ------------- REST API -------------

@app.get("/rooms/{room}/recent")
async def get_recent(room: str):
    messages = rooms_messages.get(room, [])
    return {"room": room, "messages": messages}
