# -*- coding: utf-8 -*-

from pytity.entity import Entity


class Manager(object):
    """Store and manage different objects of the entity system."""

    def __init__(self):
        self.component_store = {}
        self.processor_store = []
        self.entity_store = {}
        self.created_entities = 0

    def create_entity(self):
        """Create, store and return an entity.

        Entity is calculated by incrementing the number of created entities.

        Returns:
          An Entity (int) greater than zero.

        Example:

        >>> m = Manager()
        >>> e = m.create_entity()
        >>> e > 0 and e in list(m.entities())
        True

        """
        self.created_entities += 1
        entity = Entity(self.created_entities, self)
        self.entity_store[entity] = {}
        return entity

    def kill_entity(self, entity):
        """Kill an entity in this manager.

        Killing an entity means all its components are destroyed and its
        identifier could be reused later by using create_entity() method.
        After killing, manager entity add_component and get_component() are not
        usable anymore.

        If entity does not exist, nothing happens.

        Args:
          entity (Entity): the entity to kill.

        Raises:
          ValueError if entity does not exist.

        Example:

        >>> m = Manager()
        >>> e = m.create_entity()
        >>> m.kill_entity(e)
        >>> e not in list(m.entities())
        True

        >>> from pytity.component import Component
        >>> c = Component(42)
        >>> e.add_component(c)
        Traceback (most recent call last):
            ...
        AttributeError: 'NoneType' object has no attribute 'add_component'

        """
        # Entity doesn't exist, do nothing
        if entity not in self.entity_store:
            raise ValueError('Entity {0} does not exist'.format(entity))

        for component_type in self.entity_store[entity]:
            self.component_store[component_type].remove(entity)

        entity.manager = None
        del self.entity_store[entity]

    def entities(self):
        """Return a generator of entities.

        Returns:
          A generator of entities.

        Example:

        >>> m = Manager()
        >>> e1 = m.create_entity()
        >>> e2 = m.create_entity()
        >>> e_list = list(m.entities())
        >>> e1 in e_list and e2 in e_list
        True

        """
        for entity in self.entity_store:
            yield entity

    def entities_by_type(self, component_type):
        """Return a generator of entities for the given component type.

        If the component type does not exist, method returns immediately.

        Args:
          component_type (class): a component type to filter.

        Returns:
          A generator of entities having the given component type.

        Example:

        >>> from pytity.component import Component
        >>> m = Manager()
        >>> e = m.create_entity()
        >>> c = Component('spam')
        >>> e.add_component(c)
        >>> e_iter = m.entities_by_type(Component)
        >>> next(e_iter) == e
        True

        >>> m = Manager()
        >>> len(list(m.entities_by_type(Component)))
        0

        """
        if component_type not in self.component_store:
            return

        for entity in self.component_store[component_type]:
            yield entity

    def entities_by_types(self, component_types):
        """Return a generator of entities for given component types.

        Note that returned entities contain all the specified component types.
        If no types or one of them does not exist in manager, iterator is
        stopped immediately.

        Args:
          component_types (list of classes): is a list of component types to
                                             filter.

        Returns:
          A generator of entities having the given component types.

        Examples:

        >>> from pytity.component import Component
        >>> m = Manager()
        >>> e = m.create_entity()
        >>> c = Component('spam')
        >>> e.add_component(c)
        >>> e_iter = m.entities_by_types([Component])
        >>> next(e_iter) == e
        True

        >>> len(list(m.entities_by_types([])))
        0

        """

        if len(component_types) == 0:
            # No type? We return nothing!
            return

        for component_type in component_types:
            if component_type not in self.component_store:
                # One of the component type does not exist? It means no
                # entity can have this type and so we have to return nothing.
                return

        first_type = component_types[0]
        entities = set(self.component_store[first_type])
        for component_type in component_types[1:]:
            entities = entities.intersection(
                self.component_store[component_type]
            )

        for entity in entities:
            yield entity

    def init_component(self, component_type):
        """Init the storage for a specific component type.

        If component has previously been initialized, nothing happens.

        Args:
          component_type (class): the name of the component store to
                                  initialize.

        """
        if component_type not in self.component_store:
            self.component_store[component_type] = []

    def components_by_type(self, component_type):
        """Return a generator of component for a given component type.

        Args:
          component_type (class): a component type to filter.

        Returns:
          A generator of components having the given component type.

        Example:

        >>> from pytity.component import Component
        >>> m = Manager()
        >>> e = m.create_entity()
        >>> c = Component('spam')
        >>> e.add_component(c)
        >>> c_iter = m.components_by_type(Component)
        >>> c in c_iter
        True

        """
        for entity in self.entities_by_type(component_type):
            yield self.entity_store[entity][component_type]

    def add_component(self, entity, component):
        """Set a component to an entity.

        If entity doesn't have the corresponding component, it is added.
        If type of the component has not been initialized, it is automatically.

        Args:
          entity (Entity): the entity on which we set the component.
          component (Component): the component to attach to the entity.

        """
        if component.type not in self.component_store:
            self.init_component(component.type)

        self.component_store[component.type].append(entity)
        self.entity_store[entity][component.type] = component

    def get_component(self, entity, component_type):
        """Return the component of a given entity.

        Args:
          entity (Entity): the entity of which we want to get component value.
          component_type (class): the type of the component to get.

        Returns:
          The Component associated to the entity, None if it is not existing.

        Examples:

        >>> from pytity.component import Component
        >>> m = Manager()
        >>> e = m.create_entity()
        >>> c = Component(42)
        >>> m.add_component(e, c)
        >>> c_get = m.get_component(e, c.type)
        >>> c_get.value
        42

        >>> m = Manager()
        >>> e = m.create_entity()
        >>> c = Component(1)
        >>> m.get_component(e, c.type) is None
        True

        """
        if entity not in self.entity_store or\
                component_type not in self.entity_store[entity]:
            return None

        return self.entity_store[entity][component_type]

    def add_processor(self, processor):
        """Add a processor to the manager.

        Args:
          processor (System): the processor to add to the manager.

        """
        self.processor_store.append(processor)

    def processors(self):
        """Return a generator of processors.

        Returns:
          A generator of processors.

        """
        for processor in self.processor_store:
            yield processor

    def update(self, delta):
        """Call *update() methods on all the registered processors.

        For each processor, pre_update, update and post_update are called.

        Args:
          delta (float): a delta of time since the last update call.

        """
        for processor in self.processor_store:
            processor.pre_update(delta)
            processor.update(delta)
            processor.post_update(delta)
