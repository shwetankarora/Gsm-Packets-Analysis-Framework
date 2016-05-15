from __future__ import print_function
from twisted.internet import defer, reactor
from txmongo.connection import ConnectionPool

url = "mongodb://localhost:27017"
cursor = None


@defer.inlineCallbacks
def getConnection():
    global cursor
    cursor = yield ConnectionPool(url)


@defer.inlineCallbacks
def getHomeStates():
    # this will return pid->homezone
    population = 2000
    retVal = {}
    db = cursor.GsmSimulatedData
    col = db.RawPackets
    print('home state function called')
    for i in range(population+1):
        print('id->'+str(i))
        pid = i
        skip = 0
        limit = 100
        count = {'nw': 0, 'ne': 0, 'e': 0, 'w': 0, 'n': 0, 's': 0, 'c': 0, 'sw': 0}
        flag = False
        while True:
            docs = yield col.find(spec={'id': pid}, skip=skip, limit=limit)
            if len(docs):
                for doc in docs:
                    time = doc['time']
                    if time <= 1440 and time >= 1200:
                        count[doc['tower']['zone']] += 1
                val = max(count.values())
                for k in count.keys():
                    if count[k] == val and val >= 3:
                        flag = True
                        retVal[pid] = k
                        break
                if not flag:
                    skip += limit
                    print('loop again')
                else:
                    break
            else:
                break
    print('Home state finished')
    db = cursor.GsmSimulatedData
    col = db.PeopleHomeZones
    for k, v in retVal.items():
        yield col.insert({'id': k, 'zone': v})
    print(retVal)

if __name__ == '__main__':
    getConnection()
    getHomeStates().addCallback(lambda ign: reactor.stop())
    reactor.run()
