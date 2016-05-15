from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from txmongo.connection import ConnectionPool
from autobahn.twisted.util import sleep
import hashlib


@inlineCallbacks
def getPercentage(mongo):
    totalPop = 20000
    retVal = {}
    db = mongo.GsmSimulatedData
    col = db.RawPackets
    docs = yield col.find()
    prev_pid = -1
    for doc in docs:
        day = doc['day']
        pid = doc['id']
        time = doc['time']
        # print(time, type(time))
        if day == 0:
            if time <= 1440 and time >= 1200:
                try:
                    zone = doc['tower']['zone']
                    if prev_pid != pid:
                        retVal[zone] += 1
                except KeyError:
                    retVal[zone] = 1
                print(doc)
        else:
            print(day)
            break
        prev_pid = pid
    print(retVal)


class CellData(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        # barChart is the function name
        # _id is the topic id
        # title is the title
        # if function name == __all__ then unsubscribe to all
        yield self.publish('com.example.data', 'barChart', oneTime=True, _id=self._id, title=self.title)
        yield sleep(3)

        dat = yield getPercentage(self.mongo)
        '''
        for doc in data:
            yield self.publish('com.example.data', 'barChart', data=doc, block=0, delay=0.01, oneTime=False, _id=self._id, add=True)
            yield sleep(0.01)

        '''



    @inlineCallbacks
    def onConnect(self):
        self.url = 'mongodb://localhost:27017'
        self.mongo = yield ConnectionPool(self.url)
        self.join(self.config.realm)
        self.title = "Population in different zones"
        m = hashlib.md5()
        m.update(self.title)
        self._id = m.hexdigest()


runner = ApplicationRunner(u'ws://localhost:8080/ws', realm=u'realm1')
runner.run(CellData)
