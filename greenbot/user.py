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
    __commandContext = None # Used to prepend commands for free text inputs

    def __init__(self, uid):
        self.__uid = int(uid)

        # We'll use the default config if nothing is found
        logging.debug('Getting user data for ' + str(self.__uid))
        if os.path.isfile(self.__getConfigFileName()):
            with open(self.__getConfigFileName()) as file:
                config = json.loads(file.read())
                self.setCommandContext(config['context'])
                for identifier, settings in config['scripts'].items():
                    self.activateScript(identifier)
                    self.setScriptSchedule(identifier, greenbot.schedule.Schedule(settings['schedule']))

    def __getConfigFileName(self):
        global userPath
        return os.path.join(userPath, str(self.__uid) + '.json')

    def write(self):
        scritpsData = {}
        for identifier in self.__scripts:
            scritpsData[identifier] = {'schedule': self.getScriptSchedule(identifier).save()}
        writeme = json.dumps({
                'context' : self.__commandContext,
                'scripts' : scritpsData
            }, sort_keys=True, indent=4)
        f = open(self.__getConfigFileName(), 'w')
        f.write(writeme)
        f.close()
        return

    def activateScript(self, scriptIdentifier):
        self.__scripts.add(scriptIdentifier)
        # Preserve previous schedule (if available)
        if self.getScriptSchedule(scriptIdentifier) is not None:
            # Just reactivate it
            self.getScriptSchedule(scriptIdentifier).activate(self, scriptIdentifier)
        else:
            # Create a new one...
            self.setScriptSchedule(scriptIdentifier, greenbot.schedule.Schedule())
        self.write()
        logging.debug('Activated ' + scriptIdentifier + ' for user ' + str(self.__uid))
        return

    def deactivateScript(self, scriptIdentifier):
        self.__scripts.remove(scriptIdentifier)
        # We are not deleting the schedule data here - just in case the user deactivated the script by accident
        if self.getScriptSchedule(scriptIdentifier) is not None:
                self.getScriptSchedule(scriptIdentifier).deactivate()
        self.write()
        logging.debug('Deactivated ' + scriptIdentifier + ' for user ' + str(self.__uid))
        return

    def getScripts(self):
        return self.__scripts

    def getScriptSchedule(self, scriptIdentifier):
        if scriptIdentifier in self.__schedules:
            return self.__schedules[scriptIdentifier]
        return None

    def setScriptSchedule(self, scriptIdentifier, newSchedule):
        # Deactivate current schedule
        if self.getScriptSchedule(scriptIdentifier) is not None:
            self.getScriptSchedule(scriptIdentifier).deactivate()
        # And install new schedule
        self.__schedules[scriptIdentifier] = newSchedule
        self.write()
        newSchedule.activate(self, scriptIdentifier)
        logging.debug('Rescheduled ' + scriptIdentifier + ' for user ' + str(self.__uid))

    def getUID(self):
        return self.__uid

    def setCommandContext(self, cmd):
        self.__commandContext = cmd

    def getCommandContext(self):
        return self.__commandContext

def get(uid):
    global userCache
    # Return user from cache or load it freshly...
    if not uid in userCache:
        userCache[uid] = User(uid)
    return userCache[uid]

def getAll():
    global userCache
    global userPath
    for (root, dirs, files) in os.walk(userPath):
        for filename in files:
            if filename.endswith('.json'):
                # Okay, found a user id -> load it into the cache
                get(int(filename[:-5]))
        break
    return userCache
