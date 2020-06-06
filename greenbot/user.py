userPath = 'data/user'

class User:
    uid = None

    def __init__(self, uid):
        self.uid = uid

    def getConfig(self):
        global userPath
        logging.debug('Getting user data repos')
        os.makedirs(userPath, exist_ok=True)
        return {}

    def saveConfig(self, config):
        return

    def activateScript(self, repo, script):
        return

    def deactivateScript(self, repo, script):
        return

def get(uid):
    return User(uid)
