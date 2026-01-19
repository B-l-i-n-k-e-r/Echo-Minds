import bcrypt
from database import get_user_by_alias, add_user

def register_user(alias, password):
    existing_user = get_user_by_alias(alias)
    if existing_user:
        return False, "Alias already taken"

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    add_user(alias, hashed_password)
    return True, "User registered successfully"

def login_user(alias, password):
    user = get_user_by_alias(alias)
    
    # Security Pro-Tip: Use the same error message for "not found" 
    # and "wrong password" to protect user privacy.
    generic_error = "Invalid alias or password"

    if not user:
        return False, generic_error

    # user[2] is the password_hash column from your sqlite schema
    stored_hash = user[2] 
    
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        return True, "Login successful"
    
    return False, generic_error