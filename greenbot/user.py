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
    __scripts = set() # Stores active script identifiers
    __schedules = {} # Stores schedule information for active script identifiers

    def __init__(self, uid):
        self.__uid = int(uid)

        # We'll use the default config if nothing is found
        logging.debug('Getting user data for ' + str(self.__uid))
        if os.path.isfile(self.__getConfigFileName()):
            with open(self.__getConfigFileName()) as file:
                config = json.loads(file.read())
                for identifier, settings in config['scripts'].items():
                    self.__scripts.add(identifier)
                    self.__schedules[identifier] = greenbot.schedule.Schedule(settings['schedule'])
                    self.__schedules[identifier].activate(self, identifier)

    def __getConfigFileName(self):
        global userPath
        return os.path.join(userPath, str(self.__uid) + '.json')

    def __write(self):
        scritpsData = {}
        for identifier in self.__scripts:
            scritpsData[identifier] = {'schedule': self.getScriptSchedule(identifier).save()}
        writeme = json.dumps({
                'scripts' : scritpsData
            }, sort_keys=True, indent=4)
        f = open(self.__getConfigFileName(), 'w')
        f.write(writeme)
        f.close()
        return

    def activateScript(self, scriptIdentifier):
        self.__scripts.add(scriptIdentifier)
        self.setScriptSchedule(scriptIdentifier, self.getScriptSchedule(scriptIdentifier))
        self.getScriptSchedule(scriptIdentifier).activate()
        self.__write()
        logging.debug('Activated ' + scriptIdentifier + ' for user ' + str(self.__uid))
        return

    def deactivateScript(self, scriptIdentifier):
        self.__scripts.remove(scriptIdentifier)
        # We are not deleting the schedule data here - just in case the user deactivated the script by accident
        self.__schedules[scriptIdentifier].deactivate()
        self.__write()
        logging.debug('Deactivated ' + scriptIdentifier + ' for user ' + str(self.__uid))
        return

    def getScripts(self):
        return self.__scripts

    def getScriptSchedule(self, scriptIdentifier):
        if scriptIdentifier in self.__schedules:
            return self.__schedules[scriptIdentifier]
        return greenbot.schedule.Schedule()

    def setScriptSchedule(self, scriptIdentifier, newSchedule):
        # Deactivate current schedule
        self.__schedules[scriptIdentifier].deactivate()
        # And install new schedule
        self.__schedules[scriptIdentifier] = newSchedule
        self.__write()
        newSchedule.activate(self, scriptIdentifier)
        logging.debug('Rescheduled ' + scriptIdentifier + ' for user ' + str(self.__uid))

    def getUID(self):
        return self.__uid

def get(uid):
    global userCache
    # Return user from cache or load it freshly...
    if not uid in userCache:
        userCache[uid] = User(uid)
    return userCache[uid]
