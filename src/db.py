def setup(app_debug):
    return 'setup'

    if app_debug==True:
            logging.debug('Function : db.setup')

def close(app_debug):
    return 'close'

    if app_debug==True:
        logging.debug('Function : db.close')
