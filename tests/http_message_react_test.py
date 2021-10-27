import pytest
import requests
import json
from src import config

@pytest.fixture
def register_user1():
    requests.delete(config.url + "clear/v1")
    user = requests.post(config.url + "auth/register/v2", json = {
        'email': 'anna@gmail.com',
        'password': 'password',
        'name_first': 'anna',
        'name_last': 'li'
    })
    user_data = user.json()
    return user_data

# user 1 cerates a channel
@pytest.fixture
def user1_channel_id(register_user1):

    channel = requests.post(config.url + "channels/create/v2", json = {
        'token': register_user1['token'],
        'name': 'anna_channel',
        'is_public': False
    })
    channel_data = channel.json()
    return channel_data['channel_id']

# user 1 sends a message in channel
@pytest.fixture
def user1_channel_message_id(register_user1, user1_channel_id):

    send_message1 = requests.post(config.url + "message/send/v1", json = {
        'token': register_user1['token'],
        'channel_id': user1_channel_id,
        'message': 'hello'
    })
    message1_id = json.loads(send_message1.text)['message_id']
    return message1_id

# user1 creates a dm
def user1_dm(register_user1):
    create_dm1 = requests.post(config.url + "dm/create/v1", json = {
        'token': register_user1['token'],
        'u_ids': []
    })
    assert create_dm1.status_code == 200
    dm_id = json.loads(create_dm1.text)['dm_id']
    return dm_id

# user1 sends a message in dm
def user1_send_dm(register_user1, user1_dm):

    send_dm1_message = requests.post(config.url + "message/senddm/v1", json = {
        'token': register_user1['token'],
        'dm_id': user1_dm,
        'message': 'hello'
    })
    assert send_dm1_message.status_code == 200
    dm_message_id = json.loads(send_dm1_message.text)['message_id']
    return dm_message_id

@pytest.fixture
def register_user2():
    user2 = requests.post(config.url + "auth/register/v2", json ={
        'email': 'sallly@gmail.com',
        'password': 'password',
        'name_first': 'sally',
        'name_last': 'li'
    })
    user2_data = user2.json()
    return user2_data

# invalid token
def test_react_invalid_token(register_user1, user1_channel_message_id):
    user1_token = register_user1['token']
    message1_id = user1_channel_message_id

    requests.post(config.url + "auth/logout/v1", json = {
        'token': user1_token
    })

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': message1_id,
        'react_id': 1
    })
    assert react.status_code == 403

# message_id is not a valid message within a channel or DM that the authorised user has joined
def test_react_invalid_message_id(register_user1):
    user1_token = register_user1['token']

    # negative message_id
    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': -1,
        'react_id': 1
    })
    assert react.status_code == 400
    
    # message_id does not exist
    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': 256,
        'react_id': 1
    })
    assert react.status_code == 400

    # Access Error: invalid token and invalid message_id
    requests.post(config.url + "auth/logout/v1", json = {
        'token': user1_token
    })

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': -1,
        'react_id': 1
    })
    assert react.status_code == 403

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': 256,
        'react_id': 1
    })
    assert react.status_code == 403

# react_id is not a valid react ID - currently
# the only valid react ID the frontend has is 1
def test_react_invalid_react_id_channel(register_user1, user1_channel_message_id):
    user1_token = register_user1['token']

    # negative react_id
    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_channel_message_id,
        'react_id': -1
    })
    assert react.status_code == 400

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_channel_message_id,
        'react_id': 256
    })
    assert react.status_code == 400
    
    # Access Error: invalid token and invalid message_id
    requests.post(config.url + "auth/logout/v1", json = {
        'token': user1_token
    })

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_channel_message_id,
        'react_id': -1
    })
    assert react.status_code == 403

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_channel_message_id,
        'react_id': 256
    })
    assert react.status_code == 403

def test_react_invalid_react_id_dm(register_user1, user1_send_dm):
    user1_token = register_user1['token']

    # negative react_id
    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_send_dm,
        'react_id': -1
    })
    assert react.status_code == 400

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_send_dm,
        'react_id': 256
    })
    assert react.status_code == 400
    
    # Access Error: invalid token and invalid message_id
    requests.post(config.url + "auth/logout/v1", json = {
        'token': user1_token
    })

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_send_dm,
        'react_id': -1
    })
    assert react.status_code == 403

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_send_dm,
        'react_id': 256
    })
    assert react.status_code == 403

# the message already contains a react with ID react_id from the authorised user
def test_react_already_contain_react_id_channel(register_user1, user1_channel_message_id):
    user1_token = register_user1['token']

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_channel_message_id,
        'react_id': 1
    })
    assert react.status_code == 200

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_channel_message_id,
        'react_id': 1
    })
    assert react.status_code == 400

def test_react_already_contain_react_id_dm(register_user1, user1_send_dm):
    user1_token = register_user1['token']

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_send_dm,
        'react_id': 1
    })
    assert react.status_code == 200

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_channel_message_id,
        'react_id': 1
    })
    assert react.status_code == 400

##### Implementation #####

# valid case
def test_react_valid_channel(register_user1, user1_channel_message_id, user1_channel_id):
    user1_token = register_user1['token']

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_channel_message_id,
        'react_id': 1
    })
    assert react.status_code == 200

    messages = requests.get(config.url + "channel/messages/v2", params = {
        'token': user1_token,
        'channel_id': user1_channel_id,
        'start': 0
    })
    reaction = json.loads(messages.text)['messages'][0]['reacts'][0]['is_this_user_reacted']
    assert reaction == True

def test_react_valid_dm(register_user1, user1_dm, user1_send_dm):
    user1_token = register_user1['token']

    react = requests.post(config.url + "message/react/v1", json = {
        'token': user1_token,
        'message_id': user1_send_dm,
        'react_id': 1
    })
    assert react.status_code == 200

    message = requests.get(config.url + "dm/messages/v1",params = { 
        'token': user1_token,
        'dm_id': user1_dm, 
        'start': 0 
    })
    reaction = json.loads(message.text)['messages'][0]['reacts'][0]['is_this_user_reacted']
    assert reaction == True
