
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

if __name__ == "__main__":
    pins = FilePersister('pins.dat')

    people = ["Kennon", "Vadim", "Pooja", "Casey", "Byron", 
              "Matt", "Nick", "Miguel", "Dave", "Mark", 
             ]
    for person in people:
        pins.save(person, randomword(4))

    print pins.get_all()

    print pins.get('Kennon')
