from __future__ import print_function
from twisted.internet import defer, reactor
from txmongo.connection import ConnectionPool
from autobahn.twisted.util import sleep
import random
import math
from pymongo import MongoClient

url = "mongodb://localhost:27017"
cursor = None
packets = []
b_cursor = MongoClient()


@defer.inlineCallbacks
def getRawPackets(skip=0, limit=0):
    db = cursor.GsmSimulatedData
    col = db.RawPackets
    packets = yield col.find(skip=skip, limit=limit)
    # print(packets)
    defer.returnValue(packets)


@defer.inlineCallbacks
def getConnection(url=url):
    global cursor
    cursor = yield ConnectionPool(url)


class Epidemic():

    def __init__(self, incubation=7, totalDays=7):
        self.incubation = incubation
        self.totalDays = totalDays


class Zone():

    def __init__(self, typ, days=10, minRange=[], maxRange=[], poi=0):
        self.typeOfZone = typ
        self.minRange = minRange
        self.maxRange = maxRange
        self.days = days
        self.poi = poi  # percentage of infection spread

    # add getters and setters here

    def setAll(self, minRange, maxRange, days, poi):
        self.minRange = minRange
        self.maxRange = maxRange
        self.days = days
        self.poi = poi


class Person():

    def __init__(self, pid, i=[0, 0], cod=0, coi=0, rp=[0, 0]):
        self.pid = pid
        self.immunity = i if random.randint(i[0], i[1]) else random.randint(5, 16)
        self.cod = cod  # chance of death
        self.coi = coi if coi else random.random()  # chance of infecting
        # self.cor # chance of reinfection
        self.rp = rp if random.randint(rp[0], rp[1]) else random.randint(20, 30)
        self.infectionAfterExposure = random.randint(0, 2)
        self._infected = False
        self._symptoms = False
        self._recovery = False
        self.daysToSpread = self.immunity - self.infectionAfterExposure
        self._migration = True

    def getVariable(self, val=None):
        if val:
            if val == 'infected':
                return self._infected
            elif val == 'symptoms':
                return self._symptoms
            elif val == 'recovery':
                return self._recovery
            elif val == 'migration':
                return self._migration
            else:
                raise ValueError('Requested Variable not found')

    def set_infected(self):
        self._infected = True

    def unset_infected(self):
        self.infected = False

    def set_symptoms(self):
        self._symptoms = True

    def unset_symptoms(self):
        self.symptoms = False

    def set_recovery(self):
        self._recovery = True

    def unset_recovery(self):
        self.recovery = False

    def set_migration(self):
        self._migration = True

    def unset_migration(self):
        self.migration = False


def decision(prob):
    return random.random() < prob


def storePackets(p):
    global packets
    packets += p
    print('\033[91m', len(packets), '\033[0m')


@defer.inlineCallbacks
def waitForCompletePackets(day):
    global packets
    prev_l = -1
    # checks when to start clearing the packets

    # wait for packets to get filled
    while not len(packets):
        yield sleep(5)

    # actual check code
    while packets[-1]['day'] == day and len(packets) > prev_l:
        prev_l = len(packets)
        yield sleep(6)
        print('\033[93m Waiting for packets.... \033[0m')
    defer.returnValue(True)


@defer.inlineCallbacks
def clearPackets(day):
    global packets
    yield waitForCompletePackets(day)
    indexes = getPacketsOfDay(day)
    packets = packets[0:indexes[0]] + packets[indexes[1]+1:len(packets)]
    print("\033[92mPackets Cleared\033[0m")


@defer.inlineCallbacks
def getPacketsOfDay(day, clear=False):
    global packets
    print('Executing wait code')
    yield waitForCompletePackets(day)
    print('Done Waiting')

    # use binary search to find the packets of the day
    # print(len(packets))
    first = 0
    last = len(packets)
    mid = (last+first)/2
    # print('mid', mid)
    # print(packets[mid])
    # print(packets[-1])
    while packets[mid]['day'] != day:
        if packets[mid]['day'] > day:
            last = mid
            mid = (last + first)/2
        elif packets[mid]['day'] < day:
            first = mid
            mid = (last+first)/2

    print('\033[92mCheckpoint 1 reached\033[0m')
    # expanding mid to find the two indexes
    f_index = mid
    l_index = mid

    while True:
        try:
            if packets[f_index]['day'] == day:
                f_index -= 1
            else:
                f_index += 1
                break
        except IndexError:
            f_index += 1
            break

    while True:
        try:
            if packets[l_index]['day'] == day:
                l_index += 1
            else:
                l_index -= 1
                break
        except IndexError:
            l_index -= 1
            break

    print('\033[92mcheckpoint2 reached\033[0m')
    # print(f_index, l_index)

    retPackets = packets[f_index:l_index+1]

    if clear:
        packets = packets[0:f_index] + packets[l_index+1:len(packets)]
        print("\033[92mPackets Cleared\033[0m")

    defer.returnValue((f_index, l_index, retPackets))


def BlockingInsert(p):
    db = b_cursor.GsmSimulatedData
    col = db.ProcessedPackets
    col.insert_many(p)


id_to_homezone = {}


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
    defer.returnValue(retVal)


@defer.inlineCallbacks
def getPopulationZoneWise():
    # pop = {'<type 'str'>': <type 'int'>}
    population = 2000
    pop = {'nw': int(21.79*0.01*population),
           'ne': int(13.38*0.01*population),
           'w': int(15.2*0.01*population),
           'c': int(3.45*0.01*population),
           'e': int(10.19*0.01*population),
           'sw': int(13.68*0.01*population),
           's': int(16.32*0.01*population),
           'n': int(5.27*0.01*population)
           }
    yield sleep(0)
    defer.returnValue(pop)


@defer.inlineCallbacks
def spreadingE(pop, epidemic):
    # pop is the zonewise working population and total population
    # epidemic is the Epidemic object

    # loop for the remaining days and filter packets
    high_zone = Zone('H', days=10, minRange=[3, 5], maxRange=[40, 50], poi=0.1)
    medium_zone = Zone('M', days=10, minRange=[3, 5], maxRange=[25, 30], poi=0.05)
    low_zone = Zone('L', days=0, minRange=[0, 0], maxRange=[0, 0], poi=0.01)
    # low_zone is convertible to either of the two zones but its poi won't
    # change
    zones = {'nw': high_zone,
             'ne': medium_zone,
             's': medium_zone,
             'e': low_zone,
             'w': low_zone,
             'n': low_zone,
             'c': low_zone,
             'sw': low_zone
             }
    h_z = ['nw']
    m_z = ['ne', 's']
    # l_z = ['e', 'w', 'n', 'c', 'sw']
    persons = {}
    # infected in high and medium zone
    zones_ranges = {'nw': [random.randint(zones['nw'].minRange[0], zones['nw'].minRange[1]), random.randint(zones['nw'].maxRange[0], zones['nw'].maxRange[1])],
                    'ne': [random.randint(zones['ne'].minRange[0], zones['ne'].minRange[1]), random.randint(zones['ne'].maxRange[0], zones['ne'].maxRange[1])],
                    's':  [random.randint(zones['s'].minRange[0], zones['s'].minRange[1]), random.randint(zones['s'].maxRange[0], zones['s'].maxRange[1])]
                    }
    initially_inf = {'nw': zones_ranges['nw'][0]*0.01*pop['nw'],
                     'ne': zones_ranges['ne'][0]*0.01*pop['ne'],
                     's': zones_ranges['s'][0]*0.01*pop['s'],
                     'e': 0,
                     'w': 0,
                     'n': 0,
                     'c': 0,
                     'sw': 0
                    }
    # initially only working population will be infected
    # infection+in+working = 2.3*infection+in+non-working
    factor = 2.3
    non_working_infected = {'nw': int(math.floor(initially_inf['nw']/factor+1)),
                            'ne': int(math.floor(initially_inf['ne']/factor+1)),
                            's': int(math.floor(initially_inf['s']/factor+1)),
                            'e': 0,
                            'w': 0,
                            'n': 0,
                            'c': 0,
                            'sw': 0,
                            }
    newfac = factor/(factor+1)
    working_infected = {'nw': int(math.floor(initially_inf['nw']/newfac)),
                        'ne': int(math.floor(initially_inf['ne']/newfac)),
                        's': int(math.floor(initially_inf['s']/newfac)),
                        'e': 0,
                        'w': 0,
                        'n': 0,
                        'c': 0,
                        'sw': 0,
                        }

    dead_persons = {}

    w_i_chart = working_infected.copy()
    # id_to_homezone = yield getHomeStates()
    '''
    this code is for testing
    '''
    print('Fetching home zone data')
    global id_to_homezone
    db = cursor.GsmSimulatedData
    col = db.PeopleHomeZones
    skip = 0
    limit = 1000
    tot = yield col.count()
    for i in xrange(0, tot, limit):
        docs = yield col.find(skip=skip, limit=limit)
        skip += limit
        for doc in docs:
            id_to_homezone[doc['id']] = doc['zone']
    remaining = tot % limit
    docs = yield col.find(skip=skip, limit=remaining)
    for doc in docs:
        id_to_homezone[doc['id']] = doc['zone']
    print(len(id_to_homezone))
    print('Home zone data fetched')
    '''
    end testing
    '''

    for pid, zone in id_to_homezone.items():
        temp = Person(pid=pid, cod=0.01)
        if w_i_chart[zone]:
            w_i_chart[zone] -= 1
            temp.set_infected()
        persons[pid] = temp

    # w_i_chart = working_infected.copy()
    # nw_i_chart = non_working_infected.copy()
    coi_working = random.random()

    print('Entered in For loop')
    for i in range(epidemic.incubation, epidemic.totalDays):
        p = yield getPacketsOfDay(i, clear=True)
        print('\033[93m', len(p[2]), '\033[0m')
        print('\033[93m', p[2][0], '\033[0m')
        print('\033[93m', p[2][-1], '\033[0m')
        for piece in p[2]:
            person = persons[piece['id']]
            d_value = False
            try:
                d_value = dead_persons[piece['id']]
            except KeyError:
                d_value = False
            if not d_value and piece['tower']['zone'] != id_to_homezone[piece['id']]:
                if person.getVariable('infected'):
                    if person.daysToSpread:
                        person.daysToSpread -= 1

                        # here the person will spread infection
                        # infection will never spread from low zone to high zone
                        # or medium zone or from high zone to medium zone

                        current_zone = piece['tower']['zone']
                        try:
                            if h_z.index(current_zone):
                                continue
                            if m_z.index(current_zone):
                                continue
                        except ValueError:
                            pass

                        zonal_population = pop[current_zone]
                        infected_people = working_infected[current_zone] + non_working_infected[current_zone]
                        percentage = (infected_people/zonal_population)*100.0
                        if percentage < zones_ranges[h_z[0]][1]:
                            if decision(coi_working):
                                for pid, zone in id_to_homezone.items():
                                    if zone == current_zone:
                                        temp = persons[pid]
                                        if not temp.getVariable('infected') and not temp.getVariable('recovery'):
                                            temp.set_infected()
                                            break
                            working_infected[current_zone] += 1
                        else:
                            non_working_infected[current_zone] += 1
                    elif not person.getVariable('symptoms'):
                        person.set_symptoms()
                        person.unset_migration()
                        person.set_recovery()
                        piece['filterIt'] = 1
                    elif person.getVariable('recovery'):
                        if person.rp:
                            person.rp -= 1
                            piece['filterIt'] = 1
                        elif not decision(person.cod):
                            person.unset_infected()
                            person.unset_symptoms()
                            person.set_migration()
                        else:
                            dead_persons[piece['id']] = 1
                elif person.getVariable('recovery'):
                    person.set_migration()
                else:
                    # this is a region of non infected and non recovered. This
                    # can also spread infection on return journey but that will
                    # be done later
                    pass

        #### end of inner for loop ####

        # spreading intra_zone infection
        for k, v in zones.items():
            total_infected = working_infected[k] + non_working_infected[k]
            poi = v.poi
            new_infected = poi*total_infected
            percentage = ((total_infected+new_infected)/pop[k])*100.0
            try:
                if percentage > zones_ranges[k][1]:
                    continue
            except:
                if percentage > zones_ranges[h_z[0]][1]:
                    continue

            working = int(math.floor(new_infected*(factor/(factor+1))))
            non_working = int(math.floor(new_infected/(factor+1)))

            for pid, person in persons.items():
                if id_to_homezone[pid] == k:
                    if not person.getVariable('infected') and not person.getVariable('recovery'):
                        person.set_infected()
                        working -= 1
                if not working:
                    break

            non_working_infected[k] = non_working_infected[k] + non_working

        BlockingInsert(p[2])

    reactor.stop()


@defer.inlineCallbacks
def initiatingE():
    # original logic of filtering goes here
    # db = cursor.GsmSimulatedData
    # col = db.ProcessedPackets
    epidemic = Epidemic(totalDays=48)

    # wait till the incubation period
    for i in range(epidemic.incubation):
        p = yield getPacketsOfDay(i, clear=True)
        print('\033[93m', len(p[2]), '\033[0m')
        print('\033[93m', p[2][0], '\033[0m')
        print('\033[93m', p[2][-1], '\033[0m')
        BlockingInsert(p[2])

    getPopulationZoneWise().addCallback(spreadingE, epidemic=epidemic)


@defer.inlineCallbacks
def startFilter():
    db = cursor.GsmSimulatedData
    col = db.RawPackets
    totalPackets = yield col.count()
    # print(totalPackets, type(totalPackets))
    limit = 10000
    skip = limit
    remaining = totalPackets % limit
    # getHomeStates function is called here because it utilizes much more cpu
    # and it is called once in a program
    # global id_to_homezone
    # id_to_homezone = yield getHomeStates()
    initiatingE()
    for i in xrange(0, totalPackets-remaining+1, skip):
        yield getRawPackets(i, limit).addCallback(storePackets)
    yield getRawPackets(totalPackets-remaining, remaining).addCallback(storePackets)


def printPackets(p):
    reactor.stop()

if __name__ == '__main__':
    # getRawPackets(skip=0, limit=10).addCallback(lambda x: print(x))
    getConnection()
    startFilter()
    reactor.run()
