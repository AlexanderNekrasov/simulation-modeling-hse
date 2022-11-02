import simpy
import random

EPS = 1e-6


class Person:
    def __init__(self, p01, p8, p02, p07, name):
        assert abs(p01 + p8 - 1) < EPS
        assert abs(p02 + p07 - 1) < EPS

        self.p01 = p01 # A1->A1
        self.p8 = p8 # A1->A2
        self.p02 = p02 # A2->A2
        self.p07 = p07 # A2->A1
        self.action = "A1"  # A1 - движение, A2 - стояние
        self.name = name

    def move_forever(self, env):
        while True:
            yield env.timeout(1)
            if self.action == "A1":
                if random.random() < self.p8:
                    print("Time:", env.now, self.name, "moves from A1 to A2")
                    self.action = "A2"
                else:
                    pass
            else:
                if random.random() < self.p07:
                    print("Time:", env.now, self.name, "moves from A2 to A1")
                    self.action = "A1"
                else:
                    pass


names = ["Helen", "Alex", "Ilian", "Artem", "John", "Alice", "Bob", "Laurel", "Mike", "Carl"]

persons = list(map(lambda name: Person(0.5, 0.5, 0.5, 0.5, name), names))
env = simpy.Environment()


# def print_person_state(env):
#     yield env.timeout(1)
#     while True:
#         d = dict()
#         # print("Time: ", env.now)
#         for person in persons:
#             d[person.action] = d.get(person.action, []) + [person.name]
#         for el in d:
#             pass
#             # print(str(el) + ":", *d[el])
#         yield env.timeout(2)


for person in persons:
    env.process(person.move_forever(env))
# env.process(print_person_state(env))
env.run(until=20)
