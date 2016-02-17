# coding: utf-8

"""
This demo is about life and death of John Doe.

"""

import sys
sys.path.insert(1, '..')
import time

from pytity import Manager


is_running = True


def time_processor(manager, delta):
    try:
        person = next(manager.entities())
    except StopIteration:
        # Everybody is dead (no more entities), we should quit now...
        global is_running
        is_running = False
        return

    age = manager.get_component(person, 'age')
    life_esperancy = manager.get_component(person, 'life_esperancy')

    next_age = age + delta
    manager.publish({
        'type': 'CHANGE_AGE',
        'person': person,
        'age': next_age,
    })

    if next_age > life_esperancy:
        manager.publish({
            'type': 'KILL',
            'person': person,
        })


def grow_old(manager, action):
    manager.set_component(action['person'], 'age', action['age'])


def reaper(manager, action):
    manager.kill_entity(action['person'])


if __name__ == '__main__':
    manager = Manager()

    john_doe = manager.create_entity()
    manager.set_component(john_doe, 'name', 'John Doe')
    manager.set_component(john_doe, 'age', 0)
    manager.set_component(john_doe, 'life_esperancy', 42)

    manager.register_processor(time_processor)

    manager.register_mutator_on('CHANGE_AGE', grow_old)
    manager.register_mutator_on('KILL', reaper)

    while is_running:
        print(manager.entity_store)
        manager.update(1)
        manager.mutate()
        time.sleep(0.25)
