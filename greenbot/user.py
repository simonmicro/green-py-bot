import json

userPath = 'data/user'

# Make sure the data path exists
os.makedirs(userPath, exist_ok=True)

class User:
    uid = None
    scripts = []

    def __init__(self, uid):
        global userPath
        self.uid = uid

        # We'll default config if nothing is found
        logging.debug('Getting user data for ' + int(uid))
        fileName = os.path.join(userPath, int(uid) + '.json')
        if os.path.isfile(fileName):
            with open(fileName) as file:
                config = json.loads(file.read())
                self.scripts = config['scripts']

    def __save(self):
        return

    def activateScript(self, repo, script):
        return

    def deactivateScript(self, repo, script):
        return
