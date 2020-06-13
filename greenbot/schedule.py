import schedule
import logging
import greenbot.repos
logger = logging.getLogger('greenbot.schedule')

## Class to encapsulate all the diffenrent schedule-settings for the script of a user
class Schedule:
    __days = set([0, 1, 2, 3, 4, 5, 6]) # 0-6 are the weekdays / dayIds
    __times = set(['00:00'])
    __interval = 10
    __useInterval = False
    __jobs = []
    __forSkriptIdentifier = None
    __forUser = None
    __enabled = True

    ## Just load the provided JSON if not None
    # @param obj
    def __init__(self, obj = None):
        if obj is not None:
            self.load(obj)

    ## Load the internal state from the JSON
    # @param obj
    def load(self, obj):
        # This key was added later on...
        if 'enabled' in obj:
            self.__enabled = obj['enabled']
        self.__days = set(obj['days'])
        self.__interval = obj['interval']
        self.__useInterval = obj['useInterval']
        self.__times = set(obj['times'])

    ## Store this into serializable object
    # @return
    def save(self):
        return {
            'enabled': self.__enabled,
            'days': list(self.__days),
            'interval': self.__interval,
            'useInterval': self.__useInterval,
            'times': list(self.__times),
        }

    ## Just a wrapper for self.toString()
    # @return
    def __str__(self):
        return self.toString()

    ## Creates readible string of current settings
    # @return
    def toString(self):
        if self.__enabled:
            if self.__useInterval:
                returnme =  'every ' + str(self.__interval) + ' minute'
                if self.__interval > 1:
                    returnme = returnme + 's'
                return returnme
            return self.daysToString() + ' ' + self.timeToString()
        return 'manual only'

    ## Resolve currently active days to a readible string
    # @return
    def daysToString(self):
        if len(self.__days) == 7:
            return 'every day'
        return ', '.join(self.dayToString(x) for x in self.__days)

    ## Resolve the given day id into readible day of the week
    # @return
    @staticmethod
    def dayToString(dayId):
        if dayId == 0:
            return 'Monday'
        if dayId == 1:
            return 'Tuesday'
        if dayId == 2:
            return 'Wednesday'
        if dayId == 3:
            return 'Thursday'
        if dayId == 4:
            return 'Friday'
        if dayId == 5:
            return 'Saturday'
        if dayId == 6:
            return 'Sunday'
        return 'Unknown'

    ## Get array with currently active dayIds
    # @return
    def getDays(self):
        return self.__days

    ## Adds/Remove the given dayId to the active days. Also updates the current jobs...
    def toggleDay(self, dayId):
        if dayId in self.__days:
            self.__days.remove(dayId)
        else:
            self.__days.add(dayId)
        self.__apply()

    ## Resolve currently active time(s) to a readible string
    # @return
    def timeToString(self):
            return 'at ' + ', '.join(self.__times)

    ## Verify the timeformat by trying to apply. And, of course, add it... Also updates the current jobs...
    # @throws ValueError
    def addTime(self, time):
        self.__times.add(time)
        try:
            self.__apply()
        except schedule.ScheduleValueError:
            self.__times.remove(time)
            raise ValueError

    ## Remove the time from current trigger times. Also updates the current jobs...
    # @param time
    def removeTime(self, time):
        self.__times.remove(time)
        self.__apply()

    ## Get the current trigger times
    # @return
    def getTimes(self):
        return self.__times

    ## Sets the interval for the interval based mode. Also updates the current jobs...
    # @param interval
    def setInterval(self, interval):
        self.__interval = abs(interval)
        self.__apply()

    ## Get the current interval in minutes
    # @return
    def getInterval(self):
        return self.__interval

    ## Is this schedule active?
    # @return
    def isEnabled(self):
        return self.__enabled

    ## Enable schedule. Also updates the current jobs...
    def enable(self):
        self.__enabled = True
        self.__apply()

    ## Disable schedule. Also updates the current jobs...
    def disable(self):
        self.__enabled = False
        self.__apply()

    ## Switch to interval based. Also updates the current jobs...
    def enableInterval(self):
        self.__useInterval = True
        self.__apply()

    ## Switch to days/times based. Also updates the current jobs...
    def enableDayTime(self):
        self.__useInterval = False
        self.__apply()

    ## Is this interval based right now?
    # @return
    def usesInterval(self):
        return self.__useInterval

    ## Update current job instances
    def __apply(self):
        # First remove current jobs from the scheduler
        self.deactivate()

        # Create new job...
        if self.__enabled and self.__forUser is not None and self.__forSkriptIdentifier is not None:
            if self.__useInterval:
                self.__jobs.append(schedule.every(self.__interval).minutes.do(Schedule.run, self))
            else:
                for dayId in self.__days:
                    job = schedule.every()
                    if dayId == 0:
                        job = job.monday
                    elif dayId == 1:
                        job = job.tuesday
                    elif dayId == 2:
                        job = job.wednesday
                    elif dayId == 3:
                        job = job.thursday
                    elif dayId == 4:
                        job = job.friday
                    elif dayId == 5:
                        job = job.saturday
                    elif dayId == 6:
                        job = job.sunday
                    for time in self.__times:
                        job = job.at(time).do(Schedule.run, self)
                    self.__jobs.append(job)
            logger.info('Scheduled ' + self.__forSkriptIdentifier + ' ' + self.toString() + ' for user id ' + str(self.__forUser.getUID()))

    ## Activate this schedule. Also updates the current jobs...
    def activate(self, user, skriptIdentifier):
        # Store data for next run
        self.__forSkriptIdentifier = skriptIdentifier
        self.__forUser = user
        self.__apply()

    ## Deactivate this schedule
    def deactivate(self):
        # Remove old job (if existent)
        if len(self.__jobs) != 0:
            for job in self.__jobs:
                schedule.cancel_job(job)
            self.__jobs = []
            logger.info('Unscheduled ' + self.__forSkriptIdentifier + ' for user id ' + str(self.__forUser.getUID()))

    ## Calls the User.run() for this schedule
    def run(self):
        logger.debug('Running schedule for user id ' + str(self.__forUser.getUID()) + ', script ' + self.__forSkriptIdentifier)
        self.__forUser.runScheduled(self.__forSkriptIdentifier)
