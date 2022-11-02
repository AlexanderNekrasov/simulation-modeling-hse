import simpy

from enum import Enum
from dataclasses import dataclass
import random
import operator


def get_random_time_staying(probability_staying):
    # There is probably some better way to calculate it
    time_staying = 0
    while random.random() < probability_staying:
        time_staying += 1
    return time_staying


EPSILON = 1e-6


class Place(Enum):
    MOVING = 1
    STAYING = 2
    MOVING_IN_QUEUE = 3
    STAYING_IN_QUEUE = 4
    TERMINAL = 5


class Transition(Enum):
    ENTER_FRAME = 1  # e1
    EXIT_THROUGH_PASSPORT_CONTROL = 2  # e2
    EXIT_FRAME = 3  # e3
    ENTER_QUEUE_TAIL = 4  # e4
    ENTER_QUEUE_MIDDLE = 5  # e5
    EXIT_QUEUE = 6  # e6
    START_MOVING = 7  # e7
    STOP_MOVING = 8  # e8
    START_MOVING_IN_QUEUE = 9  # e9
    STOP_MOVING_IN_QUEUE = 10  # e10
    ENTER_QUEUE_STAYING = 11  # e11
    EXIT_QUEUE_STAYING = 12  # e12
    KEEP_MOVING = 13  # e01
    KEEP_STAYING = 14  # e02
    KEEP_MOVING_IN_QUEUE = 15  # e03
    KEEP_STAYING_IN_QUEUE = 16  # e04
    STAY_TERMINAL = 17  # ?


NEXT_PLACE = {
    Place.MOVING: {
        Transition.KEEP_MOVING: Place.MOVING,
        Transition.EXIT_FRAME: Place.TERMINAL,
        Transition.ENTER_QUEUE_TAIL: Place.MOVING_IN_QUEUE,
        Transition.ENTER_QUEUE_MIDDLE: Place.MOVING_IN_QUEUE,
        Transition.STOP_MOVING: Place.STAYING
    },
    Place.STAYING: {
        Transition.KEEP_STAYING: Place.STAYING,
        Transition.START_MOVING: Place.MOVING,
        Transition.ENTER_QUEUE_STAYING: Place.STAYING_IN_QUEUE
    },
    Place.MOVING_IN_QUEUE: {
        Transition.EXIT_THROUGH_PASSPORT_CONTROL: Place.TERMINAL,
        Transition.STOP_MOVING_IN_QUEUE: Place.STAYING_IN_QUEUE,
        Transition.KEEP_MOVING_IN_QUEUE: Place.MOVING_IN_QUEUE,
        Transition.EXIT_QUEUE: Place.MOVING,
    },
    Place.STAYING_IN_QUEUE: {
        Transition.START_MOVING_IN_QUEUE: Place.MOVING_IN_QUEUE,
        Transition.EXIT_QUEUE_STAYING: Place.STAYING,
        Transition.KEEP_STAYING_IN_QUEUE: Place.STAYING_IN_QUEUE
    },
    Place.TERMINAL: {
        Transition.STAY_TERMINAL: Place.TERMINAL,
    }
}


def next_place(current_place, transition):
    return NEXT_PLACE[current_place][transition]


@dataclass
class ProbabilityDistribution:
    probability: dict[Place, list[tuple[Transition, float]]]

    def get_transition(self, place):
        # Next place should not be the same
        new_probabilities = list(filter(lambda probability: next_place(place, probability[0]) != place,
                                   self.probability[place]))
        transitions = list(map(operator.itemgetter(0), new_probabilities))
        probabilities = list(map(operator.itemgetter(1), new_probabilities))
        return random.choices(transitions, probabilities)[0]

    def check_distribution(self):
        for place in self.probability:
            total_probability = 0
            for (transition, probability) in self.probability[place]:
                total_probability += probability
            assert abs(total_probability - 1) < EPSILON


class Person:
    def __init__(self, distribution_: ProbabilityDistribution, name_: str):
        self.distribution = distribution_
        self.name = name_

    def run(self, env):
        place = Place.MOVING_IN_QUEUE
        while True:
            probability_stay = 0
            for (transition, probability) in self.distribution.probability[place]:
                if next_place(place, transition) == place:
                    probability_stay += probability
            if probability_stay > 1 - EPSILON:
                break
            time_staying = get_random_time_staying(probability_stay)
            yield env.timeout(time_staying)
            transition = self.distribution.get_transition(place)
            assert next_place(place, transition) != place
            place = next_place(place, transition)
            print(f'{env.now}: {self.name} moved to {place}')


distribution = ProbabilityDistribution({
    Place.MOVING: [
        (Transition.KEEP_MOVING, 0.96),
        (Transition.EXIT_FRAME, 0.01),
        (Transition.ENTER_QUEUE_TAIL, 0.01),
        (Transition.ENTER_QUEUE_MIDDLE, 0.01),
        (Transition.STOP_MOVING, 0.01)
    ],
    Place.STAYING: [
        (Transition.KEEP_STAYING, 0.95),
        (Transition.START_MOVING, 0.02),
        (Transition.ENTER_QUEUE_STAYING, 0.03)
    ],
    Place.MOVING_IN_QUEUE: [
        (Transition.EXIT_THROUGH_PASSPORT_CONTROL, 0.01),
        (Transition.STOP_MOVING_IN_QUEUE, 0.33),
        (Transition.KEEP_MOVING_IN_QUEUE, 0.64),
        (Transition.EXIT_QUEUE, 0.02),
    ],
    Place.STAYING_IN_QUEUE: [
        (Transition.START_MOVING_IN_QUEUE, 0.01),
        (Transition.EXIT_QUEUE_STAYING, 0.02),
        (Transition.KEEP_STAYING_IN_QUEUE, 0.97)
    ],
    Place.TERMINAL: [
        (Transition.STAY_TERMINAL, 1)
    ]
})

distribution.check_distribution()

names = ["Helen", "Alex", "Ilian", "Artem", "John", "Alice", "Bob", "Laurel", "Mike", "Carl"]

persons = list(map(lambda name: Person(distribution, name), names))
env = simpy.Environment()

for person in persons:
    env.process(person.run(env))
env.run(until=100000)
