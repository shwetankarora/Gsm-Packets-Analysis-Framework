from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from txmongo.connection import ConnectionPool
from progressbar import ProgressBar


@inlineCallbacks
def storeLocData():

    client = ConnectionPool("mongodb://localhost:27017")
    db1 = client.GsmSimulatedData
    db2 = client.TestingData
    col = db2.PeopleLocationData

    persons = {}
    pbar = ProgressBar()

    idToHome = yield db1.PeopleHomeZones.find()

    for val in idToHome:
        persons[val['id']] = {'zone': val['zone']}

    for pid in pbar(persons.keys()):
        pac = yield db1.RawPackets.find(spec={'id': pid, 'tower.zone': persons[pid]['zone']}, limit=1)
        pac = pac[0]
        persons[pid]['loc'] = [pac['tower']['lat'], pac['tower']['lon']]
        yield col.insert_one({'id': pid, 'zone': persons[pid]['zone'], 'loc': persons[pid]['loc']})

storeLocData().addCallback(lambda ign: reactor.stop())
reactor.run()
