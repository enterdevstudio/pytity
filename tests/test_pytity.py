# -*- coding: utf-8 -*-

import pytest


def test_kill_entity_remove_component(manager):
    entity = manager.create_entity()
    manager.set_component(entity, 'component_type')

    manager.kill_entity(entity)

    assert len(manager.component_store['component_type']) == 0


def test_entities_by_types_not_return_entity_if_not_have_component(manager):
    entity = manager.create_entity()
    manager.set_component(entity, 'component_type')
    types = ['component_type', 'other_type']

    entities = list(manager.entities_by_types(types))

    assert entity not in entities


def test_register_processor(manager):
    def processor(manager, delta):
        pass

    manager.register_processor(processor)

    assert processor is next(manager.processors())


def test_register_mutator_on(manager):
    def mutator(manager, action):
        pass

    manager.register_mutator_on('ACTION_TYPE', mutator)

    assert mutator in manager.actions_to_mutators_store['ACTION_TYPE']


def test_publish(manager):
    action = {
        'type': 'ACTION_TYPE',
    }

    manager.publish(action)

    assert action is manager.actions_waiting_store.pop()


def test_publish_action_with_no_type_fails(manager):
    with pytest.raises(ValueError):
        manager.publish({})


def test_mutate(manager):
    def mutator(manager, action):
        global spy_value
        spy_value = action['payload']

    global spy_value
    spy_value = 'spam'
    manager.register_mutator_on('ACTION_TYPE', mutator)
    manager.publish({
        'type': 'ACTION_TYPE',
        'payload': 'egg',
    })

    manager.mutate()

    assert spy_value == 'egg'


def test_update(manager):
    def processor(manager, delta):
        global spy_value
        spy_value = delta

    global spy_value
    spy_value = 0
    manager.register_processor(processor)

    manager.update(0.1)

    assert spy_value == 0.1
