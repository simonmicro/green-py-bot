import os
import git
import json
import logging
import greenbot.repos
logger = logging.getLogger('greenbot.config')

token = ''
repos = {}
configPath = 'config/config.json'
version = ''

# Make sure the data path exists
os.makedirs(os.path.split(configPath)[0], exist_ok=True)

def load():
    global configPath
    global token
    global repos
    global version
    logger.debug('Loading config from ' + configPath)
    # Test if file is there...
    if not os.path.isfile(configPath):
        logger.debug('Config file not found. Creating default...')
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

    # Now determine the version hash
    try:
        version = git.Git('.').rev_parse('HEAD')[:7]
    except git.exc.GitCommandError:
        # Ooops, not running from Git... Args.
        version = '???????'

    logger.debug('Config loaded')
