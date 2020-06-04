import logging
import os
import json

token = ''
repos = {}

def load():
    global token
    global repos
    fileName = 'config.json'
    logging.debug('Loading config from ' + fileName)
    # Test if file is there...
    if not os.path.isfile(fileName):
        logging.debug('Config file not found. Creating default...')
        # If not: Create default
        defaultConfig = {
            'token' : '',
            'repos' : {}
        }
        f = open(fileName, 'w')
        f.write(json.dumps(defaultConfig, sort_keys=True, indent=4))
        f.close()

    # And load it...
    with open(fileName) as file:
        config = json.loads(file.read())
        token = config['token']
        repos = config['repos']
    logging.debug('Config loaded')
