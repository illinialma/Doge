from datetime import datetime
from enum import Enum

class Label(Enum):
    DEFAULT = 0
    TREAT = 1

    def next(self):
        return Label(1-self.value)

labels = []
curLabel = Label.DEFAULT

labels.append((curLabel.value, datetime.now()))
while 1:
    print("Current label: ", curLabel.name)
    key = input("Waiting for label change... ")
    if(key == "q"):
        break
    curLabel = curLabel.next()
    labels.append((curLabel.value, datetime.now()))

print(labels)
    