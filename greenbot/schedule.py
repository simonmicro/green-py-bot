import schedule
import logging
import greenbot.repos

class Schedule:
    __days = set([0, 1, 2, 3, 4, 5, 6]) # 0-6 are the weekdays
    __times = set(['00:00'])
    __interval = 10
    __useInterval = False
    __jobs = []
    __forSkriptIdentifier = None
    __forUser = None
    __enabled = True

    # Simple class to wrap the different parameters
    def __init__(self, obj = None):
        if obj is not None:
            self.load(obj)
        return

    def load(self, obj):
        # This key was added later on...
        if 'enabled' in obj:
            self.__enabled = obj['enabled']
        self.__days = set(obj['days'])
        self.__interval = obj['interval']
        self.__useInterval = obj['useInterval']
        self.__times = set(obj['times'])

    def save(self):
        return {
            'enabled': self.__enabled,
            'days': list(self.__days),
            'interval': self.__interval,
            'useInterval': self.__useInterval,
            'times': list(self.__times),
        }

    def __str__(self):
        return self.toString()

    def toString(self):
        if self.__enabled:
            if self.__useInterval:
                returnme =  'every ' + str(self.__interval) + ' minute'
                if self.__interval > 1:
                    returnme = returnme + 's'
                return returnme
            return self.daysToString() + ' ' + self.timeToString()
        return 'manual only'

    def daysToString(self):
        if len(self.__days) == 7:
            return 'every day'
        return ', '.join(self.dayToString(x) for x in self.__days)

    def timeToString(self):
            return 'at ' + ', '.join(self.__times)

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

    def setInterval(self, interval):
        self.__interval = abs(interval)
        self.__apply()

    def getDays(self):
        return self.__days

    def toggleDay(self, dayId):
        if dayId in self.__days:
            self.__days.remove(dayId)
        else:
            self.__days.add(dayId)
        self.__apply()

    def addTime(self, time):
        self.__times.add(time)
        try:
            self.__apply()
        except schedule.ScheduleValueError:
            self.__times.remove(time)
            raise ValueError

    def removeTime(self, time):
        self.__times.remove(time)
        self.__apply()

    def getTimes(self):
        return self.__times

    def getInterval(self):
        return self.__interval

    def isEnabled(self):
        return self.__enabled

    def enable(self):
        self.__enabled = True
        self.__apply()

    def disable(self):
        self.__enabled = False
        self.__apply()

    def enableInterval(self):
        self.__useInterval = True
        self.__apply()

    def enableDayTime(self):
        self.__useInterval = False
        self.__apply()

    def usesInterval(self):
        return self.__useInterval

    def __apply(self):
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
            logging.info('Scheduled ' + self.__forSkriptIdentifier + ' ' + self.toString() + ' for user id ' + str(self.__forUser.getUID()))

    def activate(self, user, skriptIdentifier):
        # Store data for next run
        self.__forSkriptIdentifier = skriptIdentifier
        self.__forUser = user
        self.__apply()

    def deactivate(self):
        # Remove old job (if existent)
        if len(self.__jobs) != 0:
            for job in self.__jobs:
                schedule.cancel_job(job)
            self.__jobs = []
            logging.info('Unscheduled ' + self.__forSkriptIdentifier + ' for user id ' + str(self.__forUser.getUID()))

    def run(self):
        logging.debug('Running schedule for user id ' + str(self.__forUser.getUID()) + ', script ' + self.__forSkriptIdentifier)
        self.__forUser.runScheduled(self.__forSkriptIdentifier)
