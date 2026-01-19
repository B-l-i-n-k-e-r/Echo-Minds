import bcrypt

# Store rooms: {room_name: {owner, participants, messages, is_active, password_hash}}
rooms = {}

def create_room(room_name, owner_alias, password_hash):
    if room_name in rooms:
        return False, "Room already exists"
    rooms[room_name] = {
        "owner": owner_alias,
        "participants": set(),
        "messages": [],       # Store chat history temporarily
        "is_active": True,
        "password_hash": password_hash
    }
    return True, "Room created successfully"

def join_room(room_name, user_alias, provided_password=None):
    room = rooms.get(room_name)
    if not room:
        return False, "Room does not exist"
    
    # Password check
    if provided_password:
        if not bcrypt.checkpw(provided_password.encode('utf-8'), room["password_hash"]):
            return False, "Incorrect room password"

    room["participants"].add(user_alias)
    return True, "Joined room successfully"

def leave_room(room_name, user_alias):
    room = rooms.get(room_name)
    if not room:
        return False, "Room does not exist"

    room["participants"].discard(user_alias)

    # If owner leaves, delete the room and all messages
    if user_alias == room["owner"]:
        del rooms[room_name]  # Permanently remove the room and its messages
        return True, "Room deleted as owner left"

    return True, "User left room"

def add_message(room_name, user_alias, message_text):
    room = rooms.get(room_name)
    if not room or not room["is_active"]:
        return False, "Room not active"
    
    room["messages"].append({
        "alias": user_alias,
        "message": message_text
    })
    return True, "Message added"

def get_messages(room_name):
    room = rooms.get(room_name)
    # Return all messages while room exists
    return room["messages"] if room else []
