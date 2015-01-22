# -*- coding: utf-8 -*-


class Processor(object):
    """Contain the code necessary to handle a chunk of functionality."""
    def __init__(self, needed=None):
        """Initialize a processor.

        Args:
          needed (list of str|None): a list of needed component types.

        """
        self.manager = None
        self.needed = needed

    def register_to(self, manager):
        """Register a processor to a manager.

        Set the self.manager attribute and add the processor to the given
        manager.

        Args:
          manager (Manager): the manager which will store the processor.

        Example:

        >>> from pytity.manager import Manager
        >>> m = Manager()
        >>> p = Processor()
        >>> p.register_to(m)
        >>> p is next(m.processors())
        True

        """
        self.manager = manager
        self.manager.add_processor(self)

    def pre_update(self, delta):
        """Do something before calling update()."""
        pass

    def update(self, delta):
        """Call a set of functionality.

        This method must be redifined by child classes.

        Args:
          delta (float): the delta time since the last call.

        Raises:
          NotImplementedError if method has not been implemented.

        """
        raise NotImplementedError()

    def post_update(self, delta):
        """Do something after calling update()."""
        pass


class EntityProcessor(Processor):
    """A helper class for processor which are called on a set of entities.

    This specific processor calls update() for a list of entities. Entities
    are retrieved by using self.needed list (get all entities with the needed
    components). If self.needed is None, update() is called for all the
    entities from the manager.

    """
    def update(self, delta):
        """Call update_entity() on a list of entities.

        If processor needs FooComponent (in self.needed), update_entity() will
        be called only on entities with a FooComponent.
        If self.needed is an empty list, update_entity() will not be called. In
        this case you may prefer use Processor class with update() instead of
        EntityProcessor.

        Args:
          delta (float): the delta time since the last call.

        Raises:
          AttributeError if manager has not been set.

        """
        if self.needed is not None:
            iter_entities = self.manager.entities_by_types(self.needed)
        else:
            iter_entities = self.manager.entities()

        for entity in iter_entities:
            self.update_entity(delta, entity)

    def update_entity(self, delta, entity):
        """Update a given entity.

        Args:
          delta (float): the delta time since the last call.
          entity (Entity): the entity to update.

        Raises:
          NotImplementedError if method has not been implemented.

        """
        raise NotImplementedError()
