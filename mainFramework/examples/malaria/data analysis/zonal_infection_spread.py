from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from txmongo.connection import ConnectionPool
from txmongo.collection import Collection
from autobahn.twisted.util import sleep
from progressbar import ProgressBar
import hashlib
import sys


url = "mongodb://localhost:27017"
client = None


class PublishData(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        pass

    @inlineCallbacks
    def onConnect(self):
        pass


@inlineCallbacks
def loadHomeZones():
    global client
    client = yield ConnectionPool(url)
    db = client.GsmSimulatedData
    col = db.PeopleHomeZones
    print("\033[92mLoading Home Zone data.....\033[0m")
    retVal = {}
    id_to_home = yield col.find()
    for val in id_to_home:
        retVal[val['id']] = val['zone']
    returnValue(retVal)


@inlineCallbacks
def StoreMetaData(zone, data, meta=False):
    db = client.TestingData
    if not meta:
        col = Collection(db, zone)
    else:
        col = Collection(db, zone+'_meta')

    dead = data['dead']
    infected = data['infected']
    recovered = data['recovered']

    countDead = yield col.count(spec={'dead': {'$exists': True}})
    countInf = yield col.count(spec={'infected': {'$exists': True}})
    countRec = yield col.count(spec={'recovered': {'$exists': True}})

    if dead is not None and countDead:
        docs = yield col.find(spec={'dead': {'$exists': True}})
        try:
            docs[0]['dead'].index(dead)
        except:
            yield col.update(spec={'dead': {'$exists': True}}, document={'$push': {'dead': dead}})
            d = yield col.find(spec={'countD': {'$exists': True}})
            count = int(d[0]['countD'])+1
            yield col.update(spec={'countD': {'$exists': True}}, document={'$set': {'countD': count}})
    elif not countDead and dead is not None:
        count = 1
        d = {'dead': [dead], 'countD': 1}
        yield col.insert_one(d)

    if infected is not None and countInf:
        docs = yield col.find(spec={'infected': {'$exists': True}})
        try:
            docs[0]['infected'].index(infected)
        except:
            yield col.update(spec={'infected': {'$exists': True}}, document={'$push': {'infected': infected}})
            d = yield col.find(spec={'countI': {'$exists': True}})
            count = int(d[0]['countI'])+1
            yield col.update(spec={'countI': {'$exists': True}}, document={'$set': {'countI': count}})
    elif not countInf and infected is not None:
        count = 1
        d = {'infected': [infected], 'countI': 1}
        yield col.insert_one(d)

    if recovered is not None and countRec:
        docs = yield col.find(spec={'recovered': {'$exists': True}})
        try:
            docs[0]['recovered'].index(recovered)
        except:
            yield col.update(spec={'recovered': {'$exists': True}}, document={'$push': {'recovered': recovered}})
            d = yield col.find(spec={'countR': {'$exists': True}})
            count = int(d[0]['countR'])+1
            yield col.update(spec={'countR': {'$exists': True}}, document={'$set': {'countR': count}})
    elif not countRec and recovered is not None:
        count = 1
        d = {'recovered': [recovered], 'countR': 1}
        yield col.insert_one(d)

    yield sleep(0)


@inlineCallbacks
def printDataDayWise():
    id_to_home = yield loadHomeZones()
    # id_to_home is a mapping from pid to homezone of a person
    # print id_to_home
    totalDays = int(sys.argv[1])
    global client
    db = client.GsmSimulatedData
    col = db.ProcessedPackets
    for day in range(totalDays):
        data = yield col.find(spec={'day': day})
        pbar = ProgressBar()
        for val in pbar(data):
            pid = val['id']
            try:
                if val['infected']:
                    infected = pid
            except:
                infected = None
            try:
                if val['filterIt']:
                    filterIt = pid
            except:
                filterIt = None
            try:
                if val['dead']:
                    dead = pid
            except:
                dead = None
            zone = id_to_home[pid]
            zone = zone+'_'+str(day)
            d = {'dead': dead, 'infected': infected, 'recovered': filterIt}
            yield sleep(0.005)
            StoreMetaData(zone, d, meta=True)

        print('\033[91mDay '+str(day)+' completed. Days left: '+str(totalDays-day-1)+'\033[0m')

    yield sleep(1)


if __name__ == '__main__':
    # v = loadHomeZones()
    # data = {'dead': 13, 'infected': None, 'recovered': None}
    # StoreMetaData('nw', data, meta=True)
    printDataDayWise().addCallback(lambda ign: reactor.stop())
    reactor.run()
