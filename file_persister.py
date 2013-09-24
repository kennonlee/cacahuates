
import json
import random
import string

from os import curdir, sep

class FilePersister():
    
    def __init__(self, filename):
        self.filename = filename

    def save(self, name, val):
        with open(self.filename, 'r+') as f:
            try:
                store = json.loads(f.read())
            except ValueError:
                store = {}
            print 'PERSISTING', name, val
            store[name] = val
            f.seek(0)
            f.write(json.dumps(store))
            f.truncate()
            f.close()

    def get_all(self):
        with open(self.filename, 'r+') as f:
            store = json.loads(f.read())
            f.close()
            return store

    def get(self, name):
        store = self.get_all()
        return store[name]

def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

def remove_from_all(elem):
    '''
    Removes the given element from all rankings, then persists them all. 
    Inefficient but shrug. Assumes the persisted value is a list.
    '''
    p = FilePersister("rankings.dat")
    data = p.get_all()
    for person, ranking in data.items():
        ranking.remove(elem)
        p.save(person, ranking)

def insert_for_all(elem):
    '''
    Inserts the given element into all rankings, then persists them all. 
    Inefficient but shrug. Assumes the persisted value is a list.
    '''
    p = FilePersister("rankings.dat")
    data = p.get_all()
    for person, ranking in data.items():
        ranking.append(elem)
        p.save(person, ranking)


if __name__ == "__main__":
#    pins = FilePersister('pins.dat')

#    people = ["Kennon", "Vadim", "Pooja", "Casey", "Byron", 
#              "Matt", "Nick", "Miguel", "Dave", "Mark", 
#             ]

    # round 2
#    people = ["Theresa", "Jeremy", "Eric", "Phillip", "DaveP", "Sam", "Andrew", 
#              "Souleymane"]
#    for person in people:
#        pins.save(person, randomword(4))

#    print pins.get_all()

#    print pins.get('Kennon')

#    print randomword(4)

#    insert_for_all("Athens RCSO")
#    insert_for_all("New Delhi RCSO")

    remove_from_all("Athens RCSO")
    remove_from_all("New Delhi RCSO")
