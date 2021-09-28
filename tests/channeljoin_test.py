import pytest
from src.channels import channels_create_v1
from src.channel import channel_join_v1, channel_details_v1
from src.auth import auth_register_v1
from src.data_store import data_store, initial_object
from src.other import clear_v1
from src.error import InputError, AccessError 


def test_input_invalid_channel():
    clear_v1()
    a_register = auth_register_v1('email@gmail.com', 'password', 'lily','wong')
    with pytest.raises(InputError):
        channel_join_v1(a_register, 3456)

def test_already_in(): 
    clear_v1()
    a_register = auth_register_v1('email@gmail.com', 'password', 'lily','wong')
    a_channel = channels_create_v1(a_register, 'anna', True)
    with pytest.raises(InputError): 
        channel_join_v1(a_register, a_channel)
    
def test_AccessError (): 
    clear_v1()
    a_register = auth_register_v1('email@gmail.com', 'password', 'lily','wong')
    a_channel = channels_create_v1(a_register, 'anna', False)
    j_register = auth_register_v1('ashemail@gmail.com', 'password', 'jilly','wong')
    with pytest.raises(AccessError): 
            channel_join_v1(j_register, a_channel)


def test_authuser_AccessError (): 
    clear_v1()
    a_register = auth_register_v1('email@gmail.com', 'password', 'lily','wong')
    a_channel = channels_create_v1(a_register, 'anna', True)
    with pytest.raises(AccessError):
        channel_join_v1(123, a_channel)

def test_join (): 
    clear_v1()
    a_register = auth_register_v1('email@gmail.com', 'password', 'lily','wong')
    a_channel = channels_create_v1(a_register, 'anna', True)
    j_register = auth_register_v1('ashemail@gmail.com', 'password', 'jilly','wong')
    channel_join_v1(j_register, a_channel)
    assert channel_details_v1(j_register, a_channel) == channel_details_v1(a_register, a_channel)