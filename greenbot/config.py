import json
import os

def get():
    fileName = 'config.json'
    # Test if file is there...
    if not os.path.isfile(fileName):
        # If not: Create default
        defaultConfig = {
            'token' : ''
        }
        f = open(fileName, 'w')
        f.write(json.dumps(defaultConfig))
        f.close()

    # And load it...
    with open(fileName) as file:
        return json.loads(file.read())
    return {}
