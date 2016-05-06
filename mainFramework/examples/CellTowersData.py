from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from txmongo.connection import ConnectionPool
from autobahn.twisted.util import sleep
import hashlib


@inlineCallbacks
def getDataOfTowers(mongo):
    db = mongo.GsmSimulatedData
    col = db.CellTowers
    docs = yield col.find()
    returnValue(docs)


class CellData(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        # barChart is the function name
        # _id is the topic id
        # title is the title
        # if function name == __all__ then unsubscribe to all
        yield self.publish('com.example.data', 'barChart', oneTime=True, _id=self._id, title=self.title)
        yield sleep(3)
        yield self.publish('com.example.data', 'barChart', data='hello', block=0, delay=0.01, oneTime=False, _id=self._id)
        '''
        docs = yield getDataOfTowers(self.mongo)
        for doc in docs:
            doc.pop('_id')
            yield self.publish('com.example.data', 'barChart', data=doc, block=0, delay=0.01, oneTime=False, _id=self.id)
            yield sleep(0.01)
        '''

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
