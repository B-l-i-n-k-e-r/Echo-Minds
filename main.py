from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from auth import register_user, login_user
from database import get_user_by_alias
from chat_manager import create_room, join_room, leave_room, add_message, get_messages
import bcrypt

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

sessions = {} 

# --- NEW: WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        # { "room_name": [list_of_websockets] }
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, room_name: str):
        await websocket.accept()
        if room_name not in self.active_connections:
            self.active_connections[room_name] = []
        self.active_connections[room_name].append(websocket)

    def disconnect(self, websocket: WebSocket, room_name: str):
        if room_name in self.active_connections:
            self.active_connections[room_name].remove(websocket)
            if not self.active_connections[room_name]:
                del self.active_connections[room_name]

    async def broadcast(self, room_name: str, message: dict):
        if room_name in self.active_connections:
            for connection in self.active_connections[room_name]:
                await connection.send_json(message)

manager = ConnectionManager()

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": ""})

@app.post("/register")
def register(request: Request, alias: str = Form(...), password: str = Form(...)):
    success, msg = register_user(alias, password)
    if success:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "message": msg})

@app.post("/login")
def login(request: Request, alias: str = Form(...), password: str = Form(...)):
    success, msg = login_user(alias, password)
    if success:
        session_id = alias 
        sessions[session_id] = alias
        response = RedirectResponse("/rooms", status_code=303)
        response.set_cookie(key="session_id", value=session_id)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "message": msg})

# --- NEW: Logout Route ---
@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_id")
    return response

@app.get("/rooms", response_class=HTMLResponse)
def rooms_page(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("room.html", {"request": request, "alias": sessions[session_id]})

@app.post("/create_room")
def create_room_endpoint(request: Request, room_name: str = Form(...), room_password: str = Form(...)):
    session_id = request.cookies.get("session_id")
    alias = sessions.get(session_id)
    if not alias: return RedirectResponse("/", status_code=303)

    hashed_pass = bcrypt.hashpw(room_password.encode('utf-8'), bcrypt.gensalt())
    success, msg = create_room(room_name, alias, hashed_pass)
    return templates.TemplateResponse("room.html", {"request": request, "alias": alias, "message": msg})

@app.post("/join_room")
def join_room_endpoint(request: Request, room_name: str = Form(...), room_password: str = Form(...)):
    session_id = request.cookies.get("session_id")
    alias = sessions.get(session_id)
    if not alias: return RedirectResponse("/", status_code=303)

    # Note: In Step 2 we will update chat_manager to actually verify this password
    success, msg = join_room(room_name, alias)
    if success:
        return templates.TemplateResponse("chat.html", {"request": request, "alias": alias, "room_name": room_name})
    return templates.TemplateResponse("room.html", {"request": request, "alias": alias, "message": msg})

# --- ADD THIS NEW ROUTE ---
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    # This renders the register.html file when you click the link
    return templates.TemplateResponse("register.html", {"request": request, "message": ""})

# --- KEEP YOUR EXISTING POST ROUTE ---
@app.post("/register")
def register(request: Request, alias: str = Form(...), password: str = Form(...)):
    success, msg = register_user(alias, password)
    if success:
        return RedirectResponse("/", status_code=303)
    # If registration fails, show the error on the register page, not the login page
    return templates.TemplateResponse("register.html", {"request": request, "message": msg})

# --- SHOW FORGOT PASSWORD PAGE ---
@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request, "message": ""})

# --- HANDLE RESET REQUEST ---
@app.post("/forgot-password")
def handle_reset_request(request: Request, alias: str = Form(...), email: str = Form(...)):
    # Check database for the alias
    user = get_user_by_alias(alias)
    
    if not user:
        # Alias not found in database
        return templates.TemplateResponse("forgot_password.html", {
            "request": request, 
            "message": "The Username provided does not exist.", 
            "status": "error"
        })

    # Alias exists! Use the email provided from the form input
    success_msg = f"The reset password has been sent to {email}"
    return templates.TemplateResponse("forgot_password.html", {
        "request": request, 
        "message": success_msg, 
        "status": "success"
    })
# --- UPDATED: WebSocket Broadcast ---
@app.websocket("/ws/{room_name}")
async def websocket_endpoint(websocket: WebSocket, room_name: str):
    alias = websocket.query_params.get("alias", "Anon")
    await manager.connect(websocket, room_name)
    
    try:
        while True:
            data = await websocket.receive_text()
            add_message(room_name, alias, data)
            # Broadcast to everyone in the room
            await manager.broadcast(room_name, {"alias": alias, "message": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_name)
        leave_room(room_name, alias)