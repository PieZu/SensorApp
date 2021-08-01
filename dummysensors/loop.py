from api.sensors import get_sensor_update_freq
import sched, time
from math import ceil
from threading import Thread, Timer
from api.logs import insert_log, insert_logs
import time

# dummy sensors
from dummysensors.fetch import ph, temp
class Sensor:
    def __init__(self, id, func, user=2):
        self.id = id
        self.user = user
        self.fetchValue = func
        self.frequency = get_sensor_update_freq(id)
        self.backlog = None

        self.read()
    
    def read(self):
        self.frequency = get_sensor_update_freq(self.id)
        if (self.frequency > 100):
            x = Timer(self.frequency/100, self.read)
            x.daemon = True
            x.start()
        else:
            self.backlog = []
            iterPerSec = ceil(100/self.frequency)
            for i in range(iterPerSec):
                x = Timer(self.frequency/100*i, self.readFast)
                x.daemon = True
                x.start()
            x = Timer(self.frequency/100*iterPerSec, self.read)
            x.daemon = True
            x.start()
        
        if self.backlog and len(self.backlog)>1:
            insert_logs(self.user, self.id, self.backlog)
            self.backlog = None
        else:
            insert_log(self.user, self.id, round(time.time()), self.fetchValue())

    def readFast(self):
        self.backlog.append([round(time.time()), self.fetchValue()])

temp_loop = Sensor(1, temp)
ph_loop = Sensor(2, ph)

# launch the schedulers in another thread so they dont block the main lsitening
# x = Thread(target=temp_loop.s.run)
# x.start()
# y = Thread(target=ph_loop.s.run)
# y.start()