# -*- coding: utf-8 -*-


class Component(object):
    """A Component stores data of entities.

    It must be the base class for all the different Components.

    Examples:

    >>> c = Component(42)
    >>> c.value
    42

    >>> c = Component({'spam': 'egg'})
    >>> c.value['spam']
    'egg'

    """

    def __init__(self, value):
        self.value = value
        self.type = self.__class__
