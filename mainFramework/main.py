from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from twisted.internet import reactor
import json


@inlineCallbacks
def getDataOfTowers(mongo):
    db = mongo.GsmSimulatedData
    col = db.CellTowers
    docs = yield col.find()
    returnValue(docs)


class AppSession(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        # subscribe to domain com.example.data
        try:
            yield self.subscribe(self.FormatAndPublish, u'com.example.data')
            print('Client can now receive data on com.example.data:realm1')
        except Exception as e:
            print('Cannot subscribe to topic: {0}'.format(e))
        # end

    def onDisconnect(self):
        print("Disconnected")
        if reactor.running:
            reactor.stop()

    @inlineCallbacks
    def FormatAndPublish(self, topic, **kwargs):
        '''
        block -> data is comming in blocks or bundles not one at a time
        delay -> delay for animation in case of block
        topic -> barChart, pieChart, columnChart etc
        oneTime -> this will call the handle metadata part of frontend charts
        '''
        if kwargs['oneTime']:
            if topic == '__all__':
                unsubscribe = '__all__'
                subscribe = None
                title = None
                args = {'subscribe': subscribe, 'unsubscribe': unsubscribe, 'title': title}
                yield self.publish('com.example.metadata', json.dumps(args))
            else:
                subscribe = 'com.example.'+topic+'.'+kwargs['_id']
                unsubscribe = ''
                title = kwargs['title']
                args = {'subscribe': subscribe, 'unsubscribe': unsubscribe, 'title': title}
                yield self.publish('com.example.metadata', json.dumps(args))
        else:
            publish_uri = u'com.example.'+topic+'.'+kwargs['_id']
            data = kwargs['data']
            try:
                if kwargs['block']:
                    try:
                        delay = kwargs['delay']
                        for value in data:
                            yield self.publishData(json.dumps({'__id__': kwargs['_id'], '__data__': value}), publish_uri)
                            yield sleep(delay)
                    except:
                        print("delay must be given if data packets are in block form.")
                else:
                    try:
                        yield self.publishData(json.dumps({'__id__': kwargs['_id'], '__data__': data}), publish_uri)
                    except Exception as e:
                        print(e)
            except:
                print("'block' arg is missing. Please specify the format of data packets")

    @inlineCallbacks
    def publishData(self, data, uri):
        yield self.publish(uri, str(data))
        # print(data)


# runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1")
# runner.run(AppSession)

'''

available options to the data analysis script

type of chart(bar chart, pie chart etc)
comparison of two or more same type of charts(clubbing in one graph)
    multiple data is provided for each graph
    'club' option
    result -> single clubbed chart on the same page
data of two or more scripts and combining into one
    multiple data
    'no club' option
    result -> multiple charts on the same page

'''
