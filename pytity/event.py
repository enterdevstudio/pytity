# -*- coding: utf-8 -*-


class Event(object):
    """An event run a set of functionnality at a system call publishing."""
    def __init__(self):
        self.manager = None
        self.type = self.__class__

    def register_to(self, manager):
        """Register an event to a manager.

        Set the self.manager attribute and add the event to the given manager.

        Args:
          manager (Manager): the manager which will store the event.

        """
        self.manager = manager
        self.manager.subscribe(self)

    def call(self, *args):
        """Call an event functionnality.

        This method must be redifined by child classes.

        Args:
          *args (mix): a variable number of arguments to call. See child
                       classes to know which arguments are available.

        Raises:
          NotImplementedError if method has not been implemented.

        """
        raise NotImplementedError()
