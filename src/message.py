'''
Messages implementation
'''

from src.data_store import DATASTORE, initial_object
from src.error import InputError, AccessError
from src.helper import check_valid_channel_id, check_valid_member_in_channel
from src.helper import check_valid_message_id, check_authorised_user_edit, check_valid_message
from src.server_helper import decode_token, valid_user
import time

def message_send_v1(token, channel_id, message):
    
    store = DATASTORE.get()
    valid_user(token)
    auth_user_id = decode_token(token)
    
    # Invalid channel_id
    if not check_valid_channel_id(channel_id):
        raise InputError("The channel_id does not refer to a valid channel")

    # Authorised user not a member of channel
    if not check_valid_member_in_channel(channel_id, auth_user_id):
        raise AccessError("Authorised user is not a member of channel with channel_id")

    # Invalid message: Less than 1 or over 1000 characters
    if not check_valid_message(message):
        raise InputError("Message is invalid as length of message is less than 1 or over 1000 characters.")

    # Creating unique message_id 
    message_id = (len(initial_object['messages']) * 2) + 1

    # Current time message was created and sent
    time_created = time.time()

    message_details = {
        'message_id': message_id,
        'u_id': auth_user_id, 
        'message': message,
        'time_created': time_created
    }

    # Append dictionary of message details into initial_objects['channels']['messages']
    for channel in initial_object['channels']:
        if channel['channel_id'] == channel_id:
            channel['messages'].append(message_details)

    # Append dictionary of message details into intital_objects['messages']
    message_details['channel_id'] = channel_id
    initial_object['messages'].append(message_details)

    DATASTORE.set(store)

    return {
        'message_id': message_id
    }


def message_edit_v1(token, message_id, message):

    auth_user_id = decode_token(token)
    store = DATASTORE.get()

    # Invalid message: Less than 1 or over 1000 characters
    if not check_valid_message(message):
        raise InputError("Message is invalid as length of message is less than 1 or over 1000 characters.")

    # Checks if message_id does not refer to a valid message within a channel/DM 
    # that the authorised user has joined
    if not check_valid_message_id(auth_user_id, message_id):
        raise InputError("The message_id is invalid.")
    
    # Checks if the message was sent by the authorised user making this request
    # AND/OR
    # the authorised user has owner permissions in the channel/DM
    if not check_authorised_user_edit(auth_user_id, message_id):
        raise AccessError("The user is unauthorised to edit the message.")

    
    for iterate_message in initial_object['messages']:
        if iterate_message['message_id'] == message_id:
            iterate_message['message'] = message
            
            if message_id % 2 == 1:
                channel_dm_id = iterate_message['channel_id']
            elif message_id % 2 == 0:
                channel_dm_id = iterate_message['dm_id']

    if message_id % 2 == 1:
        for channel in initial_object['channels']:
            if channel['channel_id'] == channel_dm_id:
                for iterate_message in channel['messages']:
                    if iterate_message['message_id'] == message_id:
                        iterate_message['message'] = message
                
    elif message_id % 2 == 0:
        for dm in initial_object['dms']:
            if dm['dm_id'] == channel_dm_id:
                for iterate_message in dm['messages']:
                    if iterate_message['message_id'] == message_id:
                        iterate_message['message'] = message
                        
    
    DATASTORE.set(store)