# -*- coding: utf-8 -*-

import collections


__version__ = '0.1.0'


class Manager(object):
    """Store and manage different objects of the entity system."""
    def __init__(self):
        self.component_store = {}
        self.processor_store = []
        self.actions_to_mutators_store = {}
        self.actions_waiting_store = collections.deque()
        self.entity_store = {}
        self.created_entities = 0

    def create_entity(self, schema={}):
        """Create, store and return an entity.

        Entity is calculated by incrementing the number of created entities.

        Args:
          components (dict): contains a list of components to set to the entity

        Returns:
          An Entity (int) greater than zero.

        Example:

        >>> m = Manager()
        >>> e = m.create_entity()
        >>> e > 0 and e in list(m.entities())
        True

        """
        self.created_entities = entity = self.created_entities + 1
        self.entity_store[entity] = {}
        for component_type, component_value in schema.items():
            self.set_component(entity, component_type, component_value)

        return entity

    def kill_entity(self, entity):
        """Kill an entity in this manager.

        Killing an entity means all its components are destroyed and its
        identifier could be reused later by using create_entity() method.

        Args:
          entity (int): the entity to kill.

        Raises:
          ValueError if entity does not exist.

        Example:

        >>> m = Manager()
        >>> e = m.create_entity()
        >>> m.kill_entity(e)
        >>> e not in list(m.entities())
        True

        >>> m.kill_entity(e)
        Traceback (most recent call last):
            ...
        ValueError: Entity '1' does not exist

        """
        if entity not in self.entity_store:
            raise ValueError("Entity '{0}' does not exist".format(entity))

        for component_type in self.entity_store[entity]:
            self.component_store[component_type].remove(entity)

        del self.entity_store[entity]

    def entities(self):
        """Return a generator of entities.

        Returns:
          A generator of entities.

        Example:

        >>> m = Manager()
        >>> e1 = m.create_entity()
        >>> e2 = m.create_entity()
        >>> entities = m.entities()
        >>> e1 == next(entities)
        True
        >>> e2 == next(entities)
        True

        """
        yield from self.entity_store

    def entities_by_type(self, component_type):
        """Return a generator of entities for the given component type.

        If the component type does not exist, method returns immediately.

        Args:
          component_type (string): a component type to filter.

        Returns:
          A generator of entities having the given component type.

        Example:

        >>> m = Manager()
        >>> e = m.create_entity()
        >>> m.set_component(e, 'component_type')
        >>> entities = m.entities_by_type('component_type')
        >>> next(entities) == e
        True

        >>> m = Manager()
        >>> len(list(m.entities_by_type('component_type')))
        0

        """
        if component_type not in self.component_store:
            return

        yield from self.component_store[component_type]

    def entities_by_types(self, component_types):
        """Return a generator of entities for given component types.

        Note that returned entities contain all the specified component types.
        If no types or one of them does not exist in manager, it returns
        immediately.

        Args:
          component_types (list of strings): list of component types to filter.

        Returns:
          A generator of entities having the given component types.

        Examples:

        >>> m = Manager()
        >>> e = m.create_entity()
        >>> m.set_component(e, 'component_type')
        >>> m.set_component(e, 'other_type')
        >>> entities = m.entities_by_types(['component_type', 'other_type'])
        >>> next(entities) == e
        True

        >>> len(list(m.entities_by_types([])))
        0

        """
        no_component = len(component_types) == 0
        store_component_types = self.component_store.keys()
        types_diff = set(component_types).difference(store_component_types)
        component_not_stored = len(types_diff) > 0
        if no_component or component_not_stored:
            return

        first_type = component_types[0]
        entities = set(self.component_store[first_type])
        for component_type in component_types[1:]:
            entities = entities.intersection(
                self.component_store[component_type]
            )

        yield from entities

    def set_component(self, entity, component_type, component=True):
        """Set a component to an entity.

        If entity doesn't have the corresponding component, it is added.

        Args:
          entity (int): the entity on which we set the component.
          component_type (string): the component type to attach to the entity.
          component (mixed): the component value to attach to the entity.

        Example:

        >>> m = Manager()
        >>> e = m.create_entity()
        >>> m.set_component(e, 'component_type', 42)
        >>> m.get_component(e, 'component_type') == 42
        True
        """
        if component_type not in self.component_store:
            self.component_store[component_type] = []

        if component_type not in self.entity_store[entity]:
            self.component_store[component_type].append(entity)

        self.entity_store[entity][component_type] = component

    def get_component(self, entity, component_type):
        """Return the component value of a given entity.

        Args:
          entity (int): the entity of which we want to get component value.
          component_type (string): the type of the component to get.

        Returns:
          The component value associated to the entity, None if it is not
          existing.

        Examples:

        >>> m = Manager()
        >>> e = m.create_entity()
        >>> m.set_component(e, 'component_type', 42)
        >>> component = m.get_component(e, 'component_type')
        >>> component == 42
        True

        >>> m = Manager()
        >>> e = m.create_entity()
        >>> m.get_component(e, 'component_type') is None
        True

        """
        entity_does_not_exist = entity not in self.entity_store
        has_not_component = component_type not in self.entity_store[entity]
        if entity_does_not_exist or has_not_component:
            return None

        return self.entity_store[entity][component_type]

    def register_processor(self, processor):
        """Register a processor to the manager.

        Args:
          processor (function): the processor to add to the manager.

        """
        self.processor_store.append(processor)

    def processors(self):
        """Return a generator of processors.

        Returns:
          A generator of processors.

        """
        yield from self.processor_store

    def register_mutator_on(self, action_type, mutator):
        """Register a mutator on a specific action.

        A mutator is a function taking the manager itself plus an action as
        parameters.

        Args:
            action_type (string): action that the mutator is listening to.
            mutator (function): a function that can mutate the manager state.

        """
        if action_type not in self.actions_to_mutators_store:
            self.actions_to_mutators_store[action_type] = []

        self.actions_to_mutators_store[action_type].append(mutator)

    def publish(self, action):
        """Publish an action.

        An action is a dict with, at least, a ``type`` key. It is stored in the
        actions_waiting_store until mutate is called.

        Args:
            action (dict): the action to publish

        Raises:
          ValueError if action has not a ``type`` key.

        """
        if 'type' not in action:
            raise ValueError("Action must have a 'type' key")

        self.actions_waiting_store.append(action)

    def process_waiting_actions(self):
        """Return a generator on the published actions.

        Returns:
            A generator of actions (dict)

        """
        while True:
            try:
                yield self.actions_waiting_store.popleft()
            except IndexError:
                break

    def mutate(self):
        """Call mutators according to the waiting actions.

        Actions are processed one by one and related-mutators are called then
        with manager and the action as parameterss.

        """
        for action in self.process_waiting_actions():
            for mutator in self.actions_to_mutators_store[action['type']]:
                mutator(self, action)

    def update(self, delta):
        """Call all the registered processors.

        Args:
          delta (float): a delta of time since the last update call.

        """
        for processor in self.processor_store:
            processor(self, delta)
