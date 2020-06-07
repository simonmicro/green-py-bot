import os
import json
import logging
import greenbot.schedule
import greenbot.repos

userPath = 'data/user'
userCache = {}

# Make sure the data path exists
os.makedirs(userPath, exist_ok=True)

class User:
    __uid = None
    __scripts = [] # Stores active script identifiers
    __schedules = {} # Stores schedule information for active script identifiers

    def __init__(self, uid):
        self.__uid = int(uid)

        # We'll use the default config if nothing is found
        logging.debug('Getting user data for ' + str(self.__uid))
        if os.path.isfile(self.__getConfigFileName()):
            with open(self.__getConfigFileName()) as file:
                config = json.loads(file.read())
                for identifier, settings in config['scripts']:
                    self.__scripts.append(identifier)
                    self.__schedules[identifier] = greenbot.schedule.Schedule(settings['schedule'])

    def __getConfigFileName(self):
        global userPath
        return os.path.join(userPath, str(self.__uid) + '.json')

    def __write(self):
        scritpsData = {}
        for identifier in self.__scripts:
            scritpsData[identifier] = {'schedule': self.__schedules[identifier].save()}
        writeme = json.dumps({
                'scripts' : scritpsData
            }, sort_keys=True, indent=4)
        f = open(self.__getConfigFileName(), 'w')
        f.write(writeme)
        f.close()
        return

    def activateScript(self, repo, script):
        self.__scripts.append(greenbot.repos.makeIdentifier(repo, script))
        self.setScriptSchedule(repo, script, greenbot.schedule.Schedule())
        self.__write()
        return

    def deactivateScript(self, repo, script):
        self.__scripts.remove(greenbot.repos.makeIdentifier(repo, script))
        self.__write()
        return

    def getScripts(self):
        returnme = []
        for identifier in self.__scripts:
            returnme.append(greenbot.repos.resolveIdentifier(identifier))
        return returnme

    def getScriptSchedule(self, repo, script):
        return self.__schedules[greenbot.repos.makeIdentifier(repo, script)]

    def setScriptSchedule(self, repo, script, schedule):
        self.__schedules[greenbot.repos.makeIdentifier(repo, script)] = schedule

    def getUID(self):
        return self.__uid

def get(uid):
    global userCache
    # Return user from cache or load it freshly...
    if not uid in userCache:
        userCache[uid] = User(uid)
    return userCache[uid]
