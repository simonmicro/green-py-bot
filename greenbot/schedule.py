class Schedule:
    __days = [0, 1, 2, 3, 4, 5, 6] # 0-6 are the weekdays
    __interval = 10 # Run every 10 minutes, if < 0 the times array will be used
    __times = ['00:00']

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
