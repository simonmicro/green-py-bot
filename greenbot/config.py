import logging
import os
import json

token = ''

def load():
    global token
    fileName = 'config.json'
    logging.debug('Loading config from ' + fileName)
    # Test if file is there...
    if not os.path.isfile(fileName):
        logging.debug('Config file not found. Creating default...')
        # If not: Create default
        defaultConfig = {
            'token' : ''
        }
        f = open(fileName, 'w')
        f.write(json.dumps(defaultConfig))
        f.close()

    # And load it...
    with open(fileName) as file:
        config = json.loads(file.read())
        token = config['token']
    logging.debug('Config loaded')
