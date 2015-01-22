# -*- coding: utf-8 -*-


class Entity(int):
    """Represent a container of components.

    An Entity is only an identifier to which components are added. So it is an
    integer with some specific methods to facilitate the process.

    """
    def __new__(cls, value, manager=None):
        """Create a new Entity (int).

        A manager must be attach to an Entity if you want to use Entity
        specific methods. In an ideal world, Entity are always attached to a
        manager and they are only created by them.

        Args:
          value (int): identifier of the Entity.
          manager (Manager): the manager which stores the Entity

        Returns:
          An Entity object.

        """
        cls.manager = manager
        return int.__new__(cls, value)

    def add_component(self, component):
        """Set a component to the entity.

        Entity must be attached to a manager to use this method. This method
        is only a shortcut for manager.add_component(entity, component).

        Args:
          component (Component): the component to attach to the entity.

        Raises:
          AttributeError if manager has not been set.

        """
        self.manager.add_component(self, component)

    def get_component(self, component_type):
        """Get a component from the entity.

        Entity must be attached to a manager to use this method. This method
        is only a shortcut for manager.get_component(entity, component_type).

        Args:
          component_type (class): the type of the component to get.

        Returns:
          The Component associated to the entity, None if it is not existing.

        Raises:
          AttributeError if manager has not been set.

        """
        return self.manager.get_component(self, component_type)
