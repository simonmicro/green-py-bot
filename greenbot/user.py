import os
import json
import logging

userPath = 'data/user'

# Make sure the data path exists
os.makedirs(userPath, exist_ok=True)

class User:
    uid = None
    scripts = []

    def __init__(self, uid):
        self.uid = int(uid)

        # We'll use the default config if nothing is found
        logging.debug('Getting user data for ' + str(uid))
        if os.path.isfile(self.__getConfigFileName()):
            with open(self.__getConfigFileName()) as file:
                config = json.loads(file.read())
                self.scripts = set(config['scripts'])

    def __getConfigFileName(self):
        global userPath
        return os.path.join(userPath, str(self.uid) + '.json')

    def __write(self):
        f = open(self.__getConfigFileName(), 'w')
        writeme = {
            'scripts' : self.scripts
        }
        f.write(json.dumps(writeme, sort_keys=True, indent=4))
        f.close()
        return

    def activateScript(self, repo, script):
        self.scripts.append(repo + '/' + script)
        self.__write()
        return

    def deactivateScript(self, repo, script):
        self.scripts.remove(repo + '/' + script)
        self.__write()
        return
