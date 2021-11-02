'''
Messages implementation
'''
import time
from src.data_store import get_data, save
from src.error import InputError, AccessError
from src.helper import check_valid_channel_id, check_valid_member_in_channel, check_valid_message
from src.helper import check_authorised_user_edit, check_valid_message_send_format, check_authorised_user_pin
from src.helper import get_message, get_reacts, check_valid_channel_dm_message_ids, check_valid_message_id
from src.server_helper import decode_token, valid_user

def message_send_v1(token, channel_id, message):
    '''
    Send a message from the authorised user to the channel specified by channel_id

    Arguments:
        <token>        (<string>)   - an authorisation hash
        <channel_id>   (<int>)      - unique id of a channel
        <message>      (<string>)   - the content of the message

    Exceptions:
        InputError      - Occurs when channel_id does not refer to a valid channel
                        - Occurs when length of message is less than 1 or over 1000 characters

        AccessError     - Occurs when the channel_id is valid and the authorised user is 
                        not a member of the channel
                        - Occurs when token is invalid
    Return Value:
        Returns <message_id> of a valid message
    '''

    if not valid_user(token):
        raise AccessError(description='User is not valid')

    auth_user_id = decode_token(token)
    
    # Invalid channel_id
    if not check_valid_channel_id(channel_id):
        raise InputError(description="The channel_id does not refer to a valid channel")

    # Authorised user not a member of channel
    if not check_valid_member_in_channel(channel_id, auth_user_id):
        raise AccessError(description="Authorised user is not a member of channel with channel_id")

    # Invalid message: Less than 1 or over 1000 characters
    if not check_valid_message(message):
        raise InputError(description="Message is invalid as length of message is less than 1 or over 1000 characters.")

    # Creating unique message_id 
    message_id = (len(get_data()['messages']) * 2) + 1

    # Current time message was created and sent
    time_created = int(time.time())

    is_this_user_reacted = False
    is_pinned = False
    reacts_details = {
        'react_id': 1,
        'u_ids': [],
        'is_this_user_reacted': bool(is_this_user_reacted)
    }

    message_details_channels = {
        'message_id': message_id,
        'u_id': auth_user_id, 
        'message': message,
        'time_created': time_created,
        'reacts':[reacts_details],
        'is_pinned': bool(is_pinned)
    }

    # Append dictionary of message details into initial_objects['channels']['messages']
    for channel in get_data()['channels']:
        if channel['channel_id'] == channel_id:
            channel['messages'].insert(0, message_details_channels)
            save()

    message_details_messages = {
        'message_id': message_id,
        'u_id': auth_user_id, 
        'message': message,
        'time_created': time_created,
        'channel_id': channel_id,
        'reacts':[reacts_details],
        'is_pinned': bool(is_pinned)
    }

    # Append dictionary of message details into intital_objects['messages']
    get_data()['messages'].insert(0, message_details_messages)
    save()

    return {
        'message_id': message_id
    }

def message_edit_v1(token, message_id, message):
    '''
    Given a message, update its text with new text. 

    Arguments:
        <token>        (<string>)   - an authorisation hash
        <message_id>   (<int>)      - unique id of a message
        <message>      (<string>)   - the new content of the message

    Exceptions:
        InputError      - Occurs when length of message is over 1000 characters
                        - Occurs when message_id does not refer to a valid message within a channel/DM 
                        that the authorised user has joined

        AccessError     - Occurs when message_id refers to a valid message in a joined channel/DM 
                        and none of the following are true:
                        - The message was sent by the authorised user making this request
                        - The authorised user has owner permissions in the channel/DM
                        - Occurs when token is invalid
    Return Value:
        N/A
    '''

    auth_user_id = decode_token(token)
    
    if not valid_user(token):
        raise AccessError(description='User is not valid')

    # Input and Access Error are raised -> Access Error
    # Invalid message AND (checks if message was sent by auth user making request AND/OR 
    # the authorised user has owner permissions in the channel/DM)
    if not check_valid_message_send_format(message) and not check_authorised_user_edit(auth_user_id, message_id):
        raise AccessError(description="The user is unauthorised to edit the message.")

    # Invalid message: Less than 1 or over 1000 characters
    if not check_valid_message_send_format(message):
        raise InputError(description="Message is invalid as length of message is less than 1 or over 1000 characters.")

    # Checks if message_id does not refer to a valid message within a channel/DM 
    # that the authorised user has joined
    if not check_valid_message_id(auth_user_id, message_id):
        raise InputError(description="The message_id is invalid.")

    # Checks if the message was sent by the authorised user making this request
    # AND/OR
    # the authorised user has owner permissions in the channel/DM
    if not check_authorised_user_edit(auth_user_id, message_id):
        raise AccessError(description="The user is unauthorised to edit the message.")

    for channel in get_data()['channels']:
        for iterate_message in channel['messages']:
            if iterate_message['message_id'] == message_id:
                if message == '':
                    channel['messages'].remove(iterate_message)
                else:
                    iterate_message['message'] = message
            save()

    for dm in get_data()['dms']:
        for iterate_message in dm['messages']:
            if iterate_message['message_id'] == message_id:
                if message == '':
                    dm['messages'].remove(iterate_message)
                else:
                    iterate_message['message'] = message
            save()
    return {}
    
def message_remove_v1(token, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments:
        <token>        (<string>)   - an authorisation hash
        <message_id>   (<int>)      - unique id of a message

    Exceptions:
        InputError      - Occurs when message_id does not refer to a valid message within 
                        a channel/DM that the authorised user has joined

        AccessError     - Occurs when message_id refers to a valid message in a joined channel/DM 
                        and none of the following are true:
                        - The message was sent by the authorised user making this request
                        - The authorised user has owner permissions in the channel/DM
                        - Occurs when token is invalid
    Return Value:
        N/A
    '''
    
    if not valid_user(token):
        raise AccessError(description='User is not valid')
    
    auth_user_id = decode_token(token)

    # Checks if message_id does not refer to a valid message within a channel/DM 
    # that the authorised user has joined
    if not check_valid_channel_dm_message_ids(message_id):
        raise InputError(description="The message_id is invalid.")
    
    # Checks if the message was sent by the authorised user making this request
    # AND/OR
    # the authorised user has owner permissions in the channel/DM
    if not check_authorised_user_edit(auth_user_id, message_id):
        raise AccessError(description="The user is unauthorised to edit the message.")

    # Given a message_id for a message, remove message from the channel/DM
    for channel in get_data()['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                channel['messages'].remove(message)
                save()
    
    for dm in get_data()['dms']:
        for message in dm['messages']:
            if message['message_id'] == message_id:
                dm['messages'].remove(message)
                save()
    return {}

def message_react_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, 
    add a "react" to that particular message.

    Arguments:
        <token>        (<string>)   - an authorisation hash
        <message_id>   (<int>)      - unique id of a message
        <react_id>     (<int>)      - the id of a react

    Exceptions:
        InputError      - Occurs when message_id is not a valid message within a channel or DM 
                        that the authorised user has joined
                        - Occurs when react_id is not a valid react ID
                        - Occurs when the message already contains a react with ID react_id from the authorised user

        AccessError     - Occurs when token is invalid
    
    Return Value:
        N/A
    '''
    
    # invalid token
    if not valid_user(token):
        raise AccessError(description='User is not valid')
    
    auth_user_id = decode_token(token)
    react_id = int(react_id)
    message_id = int(message_id)

    # message_id is not valid
    if not check_valid_channel_dm_message_ids(message_id):
        raise InputError(description="The message_id is invalid.")

    # react id is not valid
    if react_id != 1:
        raise InputError(description="The react_id is invalid.")
    
    react = get_reacts(message_id, react_id)
    # the message already contains a react with ID react_id
    if auth_user_id in react['u_ids']:
        raise InputError(description= "Message already contains a react with ID react_id")

    react['u_ids'].append(int(auth_user_id))
    react['is_this_user_reacted'] = True
    save()
    return {}
    
def message_unreact_v1(token, message_id, react_id):
    '''
    Given a message within a channel or DM the authorised user is part of, remove a "react" to that particular message.

    Arguments:
        <token>        (<string>)   - an authorisation hash
        <message_id>   (<int>)      - unique id of a message
        <react_id>     (<int>)      - the id of a react

    Exceptions:
        InputError      - Occurs when message_id is not a valid message within a channel or DM 
                        that the authorised user has joined
                        - Occurs when react_id is not a valid react ID
                        - Occurs when the message does not contain a react with ID react_id from the authorised user

        AccessError     - Occurs when token is invalid
    
    Return Value:
        N/A
    '''

    # invalid token
    if not valid_user(token):
        raise AccessError(description='User is not valid')
    
    auth_user_id = decode_token(token)
    react_id = int(react_id)
    message_id = int(message_id)

    # message_id is not valid
    if not check_valid_channel_dm_message_ids(message_id):
        raise InputError(description="The message_id is invalid.")

    # react id is not valid
    if react_id != 1:
        raise InputError(description="The react_id is invalid.")
    
    # the message does not contain a react with ID react_id
    react = get_reacts(message_id, react_id)
    if auth_user_id not in react['u_ids']:
        raise InputError(description= "Message already contains a react with ID react_id")

    react['u_ids'].remove(int(auth_user_id))
    react['is_this_user_reacted'] = False
    save()
    return {}

def message_pin_v1(token, message_id):
    '''
    Given a message within a channel or DM, mark it as "pinned".

    Arguments:
        <token>        (<string>)   - an authorisation hash
        <message_id>   (<int>)      - unique id of a message

    Exceptions:
        InputError      - Occurs when message_id is not a valid message within a channel or DM 
                        that the authorised user has joined
                        - Occurs when the message is already pinned

        AccessError     - Occurs when token is invalid
                        - Occurs when message_id refers to a valid message in a joined channel/DM and 
                        the authorised user does not have owner permissions in the channel/DM
    
    Return Value:
        N/A
    '''

    # invalid token
    if not valid_user(token):
        raise AccessError(description='User is not valid')
    
    auth_user_id = decode_token(token)
    message_id = int(message_id)

    # message_id refers to a valid message in a joined channel/DM and 
    # the authorised user does not have owner permissions in the channel/DM
    if not check_authorised_user_pin(message_id, auth_user_id):
        raise AccessError(description="The user is unauthorised to pin the message.")
    
    # message_id is not valid
    if not check_valid_channel_dm_message_ids(message_id):
        raise InputError(description="The message_id is invalid.")
    
    # message is already pinned
    message = get_message(message_id)
    if message['is_pinned'] == True:
        raise InputError(description="The message is already pinned.")

    message['is_pinned'] = True
    save()
    return {}
