import pymongo
import sys

client = pymongo.MongoClient()
db = client.GsmSimulatedData
packets = db.ProcessedPackets
id_to_home = db.PeopleHomeZones

zone = sys.argv[1]
day = int(sys.argv[2])

'''
pop = {'nw': int(21.79*0.01*population),
'ne': int(13.38*0.01*population),
'w': int(15.2*0.01*population),
'c': int(3.45*0.01*population),
'e': int(10.19*0.01*population),
'sw': int(13.68*0.01*population),
's': int(16.32*0.01*population),
'n': int(5.27*0.01*population)
}
'''

dead = 0
def check(pid):
    global dead
    if packets.find({'id': pid, 'day': {'$lte': day}, 'dead': 1}).count():
        dead += 1
    t = packets.find({'id': pid, 'infected': 1, 'day': {'$lt': day}}).count()
    if t:
        if packets.find({'id': pid, 'infected': 1, 'day': day}).count():
            return True
        else:
            return False
    else:
        return False

print('Checkpoint 1')
population = id_to_home.find({'zone': zone}).count()
print('Checkpoint 2')

# working_pop = pop[]
'''
for i in id_to_home.find({'zone': zone}):
    if packets.find({'id': i['id'], 'day': {'$lte': day}, 'dead': 1}).count():
        dead += 1
dead = packets.find({'tower.zone': zone, 'day': day, 'dead': 1}).count()
'''

print('Checkpoint 3')
infected = 0 # note that these are only those people whose symptoms are detected
percentage = 0.0

count = 0
for i in id_to_home.find({'zone': zone}):
    count += 1
    personId = i['id']
    print(str(count*100.0/population)+'%')
    if check(personId):
        infected += 1

percentage = str((infected*100.0)/population)+'%'

print(population, dead, infected, percentage)
