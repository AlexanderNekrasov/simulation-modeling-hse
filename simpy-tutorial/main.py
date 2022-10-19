import simpy
import random


class Person:
    def __init__(self, p01, p8, p02, p07, name):
        self.p01 = p01
        self.p8 = p8
        self.p02 = p02
        self.p07 = p07
        self.action = "A1"
        self.name = name

    def move_forever(self, env):
        while True:
            yield env.timeout(2)
            if self.action == "A1":
                if random.random() < self.p8:
                    self.action = "A2"
                else:
                    pass
            else:
                if random.random() < self.p07:
                    self.action = "A1"
                else:
                    pass


names = ["Helen", "Alex", "Ilian", "Artem", "John", "Alice", "Bob", "Laurel", "Mike", "Carl"]

persons = list(map(lambda name: Person(0.5, 0.5, 0.5, 0.5, name), names))
env = simpy.Environment()


def print_person_positions(env):
    yield env.timeout(1)
    while True:
        d = dict()
        print("Time: ", env.now)
        for person in persons:
            d[person.action] = d.get(person.action, []) + [person.name]
        for el in d:
            print(str(el) + ":", *d[el])
        yield env.timeout(2)


for person in persons:
    env.process(person.move_forever(env))
env.process(print_person_positions(env))
env.run(until=20)
