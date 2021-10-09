import pytest
from src.channels import channels_create_v2
from src.channel import channel_invite_v2, channel_removeowner_v1, channel_details_v2, channel_addowner_v1
from src.error import AccessError, InputError
from src.other import clear_v1
from src.auth import auth_register_v2

def test_removeowner_invalid_channel_id():
    '''
    Invalid channel_id
    '''
    clear_v1()
    id1 = auth_register_v2('email@gmail.com', 'password', 'afirst', 'alast')
    id2 = auth_register_v2('abc@gmail.com', 'password', 'afirst', 'alast')
    with pytest.raises(InputError):
        channel_removeowner_v1(id1['token'], -1, id2['auth_user_id'])
    with pytest.raises(InputError):
        channel_removeowner_v1(id1['token'], 0, id2['auth_user_id'])
    with pytest.raises(InputError):
        channel_removeowner_v1(id1['token'], 256, id2['auth_user_id'])
    with pytest.raises(InputError):
        channel_removeowner_v1(id1['token'], 'not_an_id', id2['auth_user_id'])
    with pytest.raises(InputError):
        channel_removeowner_v1(id1['token'], '', id2['auth_user_id'])

def test_removeowner_invalid_u_id():
    '''
    Invaid u_id
    '''
    clear_v1()
    id2 = auth_register_v2('abc@gmail.com', 'password', 'afirst', 'alast')
    channel_id2 = channels_create_v2(id2['token'], 'anna', True)

    with pytest.raises(InputError):
        channel_removeowner_v1(id2['token'], channel_id2['channel_id'], -16)
    with pytest.raises(InputError):
        channel_removeowner_v1(id2['token'], channel_id2['channel_id'], 0)
    with pytest.raises(InputError):
        channel_removeowner_v1(id2['token'], channel_id2['channel_id'], 256)
    with pytest.raises(InputError):
        channel_removeowner_v1(id2['token'], channel_id2['channel_id'], 'not_an_id')
    with pytest.raises(InputError):
        channel_removeowner_v1(id2['token'], channel_id2['channel_id'], '')

def test_removeowner_invalid_owner_u_id():
    '''
    u_id refers to a user who is not an owner of the channel
    u_id refers to a user who is currently the only owner of the channel
    '''
    clear_v1()
    id2 = auth_register_v2('abc@gmail.com', 'password', 'afirst', 'alast')
    id4 = auth_register_v2('cat@gmail.com', 'password', 'bfirst', 'blast')
    channel_id2 = channels_create_v2(id2['token'], 'anna', True)
    channel_invite_v2(id2['token'], channel_id2['channel_id'], id4['auth_user_id'])
    with pytest.raises(InputError):
        channel_removeowner_v1(id2['token'], channel_id2['channel_id'], id4['auth_user_id'])
    with pytest.raises(InputError):
        channel_removeowner_v1(id2['token'], channel_id2['channel_id'], id2['auth_user_id'])

def test_removeowener_no_permission():
    '''
    channel_id is valid and the authorised user does not have owner permissions in the channel
    '''
    clear_v1()
    id2 = auth_register_v2('abc@gmail.com', 'password', 'afirst', 'alast')
    id4 = auth_register_v2('cat@gmail.com', 'password', 'bfirst', 'blast')
    channel_id2 = channels_create_v2(id2['token'], 'anna', True)
    channel_invite_v2(id2['token'], channel_id2['channel_id'], id4['auth_user_id'])

    with pytest.raises(AccessError):    
        channel_removeowner_v1(id2['token'], channel_id2['channel_id'], id2['auth_user_id'])

def test_remove_owner_valid():
    clear_v1()
    id1 = auth_register_v2('abc@gmail.com', 'password', 'afirst', 'alast')
    id2 = auth_register_v2('email@gmail.com', 'password', 'bfirst', 'blast')
    channel_id2 = channels_create_v2(id2['token'], 'anna', True)

    channel_addowner_v1(id2['token'], channel_id2['channel_id'], id1['auth_user_id'])
    details1 = channel_details_v2(id1['token'], channel_id2['channel_id'])
    assert len(details1['owner_members']) == 2

    channel_removeowner_v1(id2['token'], channel_id2['channel_id'], id1['auth_user_id'])
    details = channel_details_v2(id1['token'], channel_id2['channel_id'])
    assert len(details['owner_members']) == 1
