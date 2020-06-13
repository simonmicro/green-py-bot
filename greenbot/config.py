import logging
import os
import json
import greenbot.repos

token = ''
repos = {}
configPath = 'data/config.json'

# Make sure the data path exists
os.makedirs(os.path.split(configPath)[0], exist_ok=True)

def load():
    global configPath
    global token
    global repos
    logging.debug('Loading config from ' + configPath)
    # Test if file is there...
    if not os.path.isfile(configPath):
        logging.debug('Config file not found. Creating default...')
        # If not: Create default
        defaultConfig = {
            'token' : '',
            'repos' : {'official':''}
        }
        f = open(configPath, 'w')
        f.write(json.dumps(defaultConfig, sort_keys=True, indent=4))
        f.close()

    # And load it...
    with open(configPath) as file:
        config = json.loads(file.read())
        token = config['token']
        repos = config['repos']

    logging.debug('Config loaded')
