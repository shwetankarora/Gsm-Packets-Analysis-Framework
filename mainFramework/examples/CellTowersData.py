from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from txmongo.connection import ConnectionPool
from autobahn.twisted.util import sleep
from progressbar import ProgressBar
import hashlib


idToHome = {}
@inlineCallbacks
def getStoredPackets(mongo):
    global idToHome

    db = mongo.GsmSimulatedData
    col = db.ProcessedPackets

    docs = yield col.find(spec={'day': {'$gte': 7}})
    returnValue(docs)


class CellData(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        global idToHome
        db = self.mongo.GsmSimulatedData
        persons = {}

        idToHome = yield db.PeopleHomeZones.find()

        for val in idToHome:
            persons[val['id']] = {'zone': val['zone']}

        l = ['e', 'w', 'n', 's', 'ne', 'nw', 'sw', 'c']
        totalDays = 120
        db = self.mongo.TestingData
        print('Loading Data...')
        pbar = ProgressBar()
        for pid in pbar(persons.keys()):
            doc = yield db.PeopleLocationData.find(spec={'id': pid})
            doc = doc[0]
            doc['_id'] = 10
            persons[pid] = {'zone': doc['zone'], 'loc': doc['loc']}

        # print(persons)
        print('Loaded')

        infected = {}
        recovered = {}
        temp = {}

        print('Start')
        for ghj in l[1:2]:
            for day in range(totalDays):
                for z in l:
                    n = z+'_'+str(day)+'_meta'
                    col = db[n]
                    docs = yield col.find()
                    for doc in docs:
                        doc['_id'] = 10
                        try:
                            pids = doc['infected']
                        except:
                            continue
                        for pid in pids:
                            try:
                                infected[z]
                            except:
                                infected[z] = []
                            try:
                                infected[z].index(pid)
                                try:
                                    temp[z].remove(temp[temp.index(pid)])
                                except:
                                    pass
                            except:
                                print persons[pid]
                                yield self.publish('com.example.geochart.yo', persons[pid], infected=True)
                                yield sleep(0.1)
                                infected[z].append(pid)
                        try:
                            temp[z]
                        except:
                            temp[z] = []
                        for pid in temp[z]:
                            try:
                                recovered[z]
                            except:
                                recovered[z] = []
                            try:
                                recovered[z].index(pid)
                            except:
                                print(persons[pid])
                                yield self.publish('com.example.geochart.yo', persons[pid], infected=False)
                                yield sleep(0.1)
                                recovered[z].append(pid)

                        temp = infected.copy()


    @inlineCallbacks
    def onConnect(self):
        self.url = 'mongodb://localhost:27017'
        self.mongo = yield ConnectionPool(self.url)
        self.join(self.config.realm)
        self.title = "Test Data"
        m = hashlib.md5()
        m.update(self.title)
        self._id = m.hexdigest()


runner = ApplicationRunner(u'ws://localhost:8080/ws', realm=u'realm1')
runner.run(CellData)
