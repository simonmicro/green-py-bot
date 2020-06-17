import os
import json
import logging
import greenbot.schedule
import greenbot.repos
logger = logging.getLogger('greenbot.user')

userPath = 'config/user'
userCache = {}

# Make sure the data path exists
os.makedirs(userPath, exist_ok=True)

## Represents the user with all of his scrpts, schedules and settings
class User:
    __uid = None
    __scripts = set() # Stores active script identifiers
    __schedules = {} # Stores schedule information for active script identifiers
    __lastRunResults = {} # Stores the last execution state for a script identifier 0 = Failed, 1 = Success, * = Warning
    __commandContext = None # Used to prepend commands for free text inputs

    ## Load the user from diks (or create default instance if new)
    # @param uid
    def __init__(self, uid):
        self.__uid = int(uid)

        # We'll use the default config if nothing is found
        logger.debug('Getting user ' + str(self.__uid) + ' from ' + self.__getConfigFileName())
        if os.path.isfile(self.__getConfigFileName()):
            with open(self.__getConfigFileName()) as file:
                config = json.loads(file.read())
                self.setCommandContext(config['context'])
                for identifier, settings in config['scripts'].items():
                    self.activateScript(identifier)
                    self.setScriptSchedule(identifier, greenbot.schedule.Schedule(settings['schedule']))

    ## Create data filename for this user
    # @return
    def __getConfigFileName(self):
        global userPath
        return os.path.join(userPath, str(self.__uid) + '.json')

    ## Store the user to disk (with schedule etc)
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

    ## Has this user that identifier active?
    # @param scriptIdentifier
    def hasScript(self, scriptIdentifier):
        return scriptIdentifier in self.__scripts

    ## Activates this identifier with a default schedule
    # @param scriptIdentifier
    def activateScript(self, scriptIdentifier):
        self.__scripts.add(scriptIdentifier)
        # Preserve previous schedule (if available)
        currSched = self.getScriptSchedule(scriptIdentifier)
        if currSched is not None:
            # Just reactivate it
            currSched.link(self, scriptIdentifier)
            currSched.enable()
        else:
            # Create a new one...
            self.setScriptSchedule(scriptIdentifier, greenbot.schedule.Schedule())
        self.write()
        logger.debug('Activated ' + scriptIdentifier + ' for user ' + str(self.__uid))

    ## Deactivate this identifier and schedule for this user
    # @param scriptIdentifier
    def deactivateScript(self, scriptIdentifier):
        self.__scripts.remove(scriptIdentifier)
        if scriptIdentifier in self.__lastRunResults:
            del self.__lastRunResults[scriptIdentifier]
        # We are not deleting the schedule data here - just in case the user deactivated the script by accident
        currSched = self.getScriptSchedule(scriptIdentifier)
        if currSched is not None:
            currSched.disable()
        self.write()
        logger.debug('Deactivated ' + scriptIdentifier + ' for user ' + str(self.__uid))

    ## What identifiers are currently active?
    # @return
    def getScripts(self):
        return self.__scripts

    ## Get the Schedule instance for the script
    # @return None if not found
    def getScriptSchedule(self, scriptIdentifier):
        if scriptIdentifier in self.__schedules:
            return self.__schedules[scriptIdentifier]
        return None

    ## Change the schedule for the identifier
    def setScriptSchedule(self, scriptIdentifier, newSchedule):
        # Deactivate current schedule
        currSched = self.getScriptSchedule(scriptIdentifier)
        if currSched is not None:
            currSched.disable()
        # And install new schedule
        self.__schedules[scriptIdentifier] = newSchedule
        self.write()
        newSchedule.link(self, scriptIdentifier)
        logger.debug('Rescheduled ' + scriptIdentifier + ' for user ' + str(self.__uid))

    ## Get chat id / user id
    # @return
    def getUID(self):
        return self.__uid

    ## Update the context for the next direct messages
    # @param cmd
    def setCommandContext(self, cmd):
        self.__commandContext = cmd
        self.write()

    ## Get current context
    # @return None if not set
    def getCommandContext(self):
        return self.__commandContext

    ## Executes the manualRun(user, update, context) for the script identifier
    # @param scriptIdentifier
    # @param update
    # @param context
    def runManually(self, scriptIdentifier, update, context):
        logger.debug('Executing ' + scriptIdentifier + ' for user ' + str(self.__uid) + ' MANUALLY')
        try:
            # Load the module
            module = greenbot.repos.getModule(scriptIdentifier)

            # And call the scheduled function (if available)
            if hasattr(module, 'manualRun'):
                module.manualRun(self, update, context)
            else:
                logger.warn('Ooops, the script ' + scriptIdentifier + ' has no manualRun(user, update, context) method!')
            self.__lastRunResults[scriptIdentifier] = 1
        except:
            logger.error('An error occured at manualRun(user, update, context) of script ' + scriptIdentifier + '!')
            self.__lastRunResults[scriptIdentifier] = 0
            pass

    ## Executes the manualRun(user, update, context) for the script identifier
    # @param scriptIdentifier
    def runScheduled(self, scriptIdentifier):
        logger.debug('Executing ' + scriptIdentifier + ' for user ' + str(self.__uid) + ' SCHEDULED')
        try:
            # Load the module
            module = greenbot.repos.getModule(scriptIdentifier)

            # And call the scheduled function (if available)
            if hasattr(module, 'scheduledRun'):
                module.scheduledRun(self)
            else:
                logger.warn('Ooops, the script ' + scriptIdentifier + ' has no scheduledRun(user) method!')
            self.__lastRunResults[scriptIdentifier] = 1
        except:
            logger.error('An error occured at scheduledRun(user) of script ' + scriptIdentifier + '!')
            self.__lastRunResults[scriptIdentifier] = 0
            pass

    ## Get an emoji representing the last execution result of the identifier
    # @return ✅/⚠️/❌/🔥
    def getLastRunEmoji(self, scriptIdentifier):
        if scriptIdentifier not in self.__lastRunResults:
            return '⚠️'
        if self.__lastRunResults[scriptIdentifier] == 0:
            return '❌'
        elif self.__lastRunResults[scriptIdentifier] == 1:
            return '✅'
        else:
            return '🔥'

## Get the user instance from cache or load it into it...
def get(uid):
    global userCache
    # Return user from cache or load it freshly...
    if not uid in userCache:
        userCache[uid] = User(uid)
    return userCache[uid]

## Loads all users stored from disk or cache if available...
def getAll():
    global userCache
    global userPath
    if len(userCache) < 1:
        for (root, dirs, files) in os.walk(userPath):
            for filename in files:
                if filename.endswith('.json'):
                    # Okay, found a user id -> load it into the cache
                    get(int(filename[:-5]))
            break
    return userCache
