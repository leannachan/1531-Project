from data_store import data_store, initial_object

def clear_v1():
    '''
    Clear the data that has been stored
    '''
    store = data_store.get()
    initial_object['users'] = []
    initial_object['channels'] = []
    data_store.set(store)

    return {
    }
