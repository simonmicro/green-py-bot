import os
import json
import logging

userPath = 'data/user'

# Make sure the data path exists
os.makedirs(userPath, exist_ok=True)

class User:
    __uid = None
    __scripts = []

    def __init__(self, uid):
        self.__uid = int(uid)

        # We'll use the default config if nothing is found
        logging.debug('Getting user data for ' + str(self.__uid))
        if os.path.isfile(self.__getConfigFileName()):
            with open(self.__getConfigFileName()) as file:
                config = json.loads(file.read())
                self.__scripts = list(set(config['scripts']))

    def __getConfigFileName(self):
        global userPath
        return os.path.join(userPath, str(self.__uid) + '.json')

    def __write(self):
        f = open(self.__getConfigFileName(), 'w')
        writeme = {
            'scripts' : self.__scripts
        }
        f.write(json.dumps(writeme, sort_keys=True, indent=4))
        f.close()
        return

    def activateScript(self, repo, script):
        self.__scripts.append(repo + '/' + script)
        self.__write()
        return

    def deactivateScript(self, repo, script):
        self.__scripts.remove(repo + '/' + script)
        self.__write()
        return

    def getScripts(self):
        returnme = []
        for path in self.__scripts:
            returnme.append(path.split('/'))
        return returnme

    def getUID(self):
        return self.__uid
