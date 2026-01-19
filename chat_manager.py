import bcrypt

rooms = {}  # {room_name: {owner, participants, messages, is_active, password_hash}}

def create_room(room_name, owner_alias, password_hash):
    if room_name in rooms:
        return False, "Room already exists"
    rooms[room_name] = {
        "owner": owner_alias,
        "participants": set(),
        "messages": [],
        "is_active": True,
        "password_hash": password_hash 
    }
    return True, "Room created successfully"

# UPDATED: Added password check
def join_room(room_name, user_alias, provided_password=None):
    room = rooms.get(room_name)
    if not room:
        return False, "Room does not exist"
    
    # If a password was provided (from the form), check it
    if provided_password:
        if not bcrypt.checkpw(provided_password.encode('utf-8'), room["password_hash"]):
            return False, "Incorrect room password"

    room["participants"].add(user_alias)
    return True, "Joined room successfully"

def leave_room(room_name, user_alias):
    room = rooms.get(room_name)
    if not room: return False, "Room does not exist"

    if user_alias in room["participants"]:
        room["participants"].remove(user_alias)

    if user_alias == room["owner"]:
        # Optional: Decide if you want to keep the room alive or kill it
        room["is_active"] = False 
    return True, "User left room"

def add_message(room_name, user_alias, message_text):
    room = rooms.get(room_name)
    if not room or not room["is_active"]:
        return False, "Room not active"
    room["messages"].append({"alias": user_alias, "message": message_text})
    return True, "Message added"

def get_messages(room_name):
    room = rooms.get(room_name)
    return room["messages"] if room else []