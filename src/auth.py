from src.data_store import data_store
from src.error import InputError
import re

def auth_login_v1(email, password):
    return {
        'auth_user_id': 1,
    }

def auth_register_v1(email, password, name_first, name_last):
    store = data_store.get()

    # Error handling
    token = r'\b^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$\b'
    if not (re.search(token, email)):
        raise InputError("This email is of invalid form")

    for user in store['users']:
        if user == email:
           raise InputError("This email address has already been registered by another user") 

    if len(password) < 6:
         raise InputError("This password is less then 6 characters in length")

    if len(name_first) not in range(1, 51):
         raise InputError("name_first is not between 1 - 50 characters in length")

    if len(name_last) not in range(1, 51):
         raise InputError("name_last is not between 1 - 50 characters in length")
         
    user_id = len(store['users'])
    store['users'].append(email)

    handle = (name_first + name_last).lower()
    handle = re.sub(r'[^a-z0-9]', '', handle)
    if len(handle) > 20:
        handle = handle[0:20]
    
    store['users'].append({email, handle})
    
    number = 0
    for user in store['users']:
        if user == handle:
            handle = handle + str(number)
            number += 1
            if number == 10:
                number = 0
    
    store['users'].append({email, handle})
    data_store.set(store)

    return {
        'auth_user_id': user_id,
    }
