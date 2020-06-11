import schedule
import logging
import greenbot.repos

class Schedule:
    __days = [0, 1, 2, 3, 4, 5, 6] # 0-6 are the weekdays
    __interval = 10 # Run every 10 minutes, if < 0 the times array will be used
    __times = ['00:00']
    __job = None
    __forSkriptIdentifier = None
    __forUser = None
    __lastRunResult = 1 # 0 = Success, 1 = Warning, 2 = Failed

    # Simple class to wrap the different parameters
    def __init__(self, obj = None):
        if obj is not None:
            self.load(obj)
        return

    def load(self, obj):
        self.__days = obj['days']
        self.__interval = obj['interval']
        self.__times = obj['times']

    def save(self):
        return {
            'days': self.__days,
            'interval': self.__interval,
            'times': self.__times,
        }

    def __str__(self):
        return 'days: ' + str(self.__days) + ' times: ' + str(self.__times) + ' or interval: ' + str(self.__interval)

    def setInterval(self, interval):
        self.__interval = interval
        self.__apply()

    def getInterval(self):
        return self.__interval

    def __apply(self):
        self.deactivate()

        # Create new job...
        if self.__forUser is not None and self.__forSkriptIdentifier is not None:
            self.__job = schedule.every().minute.do(Schedule.run, self)
            logging.debug('Activated schedule for user id ' + str(self.__forUser.getUID()) + ', script ' + self.__forSkriptIdentifier)

    def activate(self, user, skriptIdentifier):
        # Store data for next run
        self.__forSkriptIdentifier = skriptIdentifier
        self.__forUser = user

        # Apply new info
        self.__apply()

    def deactivate(self):
        # Remove old job (if existent)
        if self.__job is not None:
            schedule.cancel_job(self.__job)
            self.__job = None
            logging.debug('Deactivated schedule for user id ' + str(self.__forUser.getUID()) + ', script ' + self.__forSkriptIdentifier)

    def getLastRunEmoji(self):
        if self.__lastRunResult == 0:
            return '✅'
        elif self.__lastRunResult == 1:
            return '⚠️'
        elif self.__lastRunResult == 2:
            return '❌'
        else:
            return '🔥'

    def run(self):
        logging.debug('Running schedule for user id ' + str(self.__forUser.getUID()) + ', script ' + self.__forSkriptIdentifier)
        try:
            # Load the module
            module = greenbot.repos.getModule(self.__forSkriptIdentifier)

            # And call the scheduled function (if available)
            if hasattr(module, 'scheduledRun'):
                module.scheduledRun(self.__forUser)
                self.__lastRunResult = 0
            else:
                logging.error('Ooops, the script ' + self.__forSkriptIdentifier + ' has no scheduledRun(user) method!')
        except:
            self.__lastRunResult = 2
            pass
