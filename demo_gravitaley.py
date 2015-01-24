# -*- coding: utf-8 -*-

"""
This demo shows a simple example to show how to use pytity in your project.
It is highly based on libes demo, another entity system library (in C++). All
the credits go to its author!

https://github.com/jube/libes

"""

import os
import random

import pygame

from pytity.component import Component
from pytity.processor import Processor, EntityProcessor
from pytity.event import Event
from pytity.manager import Manager


GRAVITY = 200
RADIUS = 24
LOSS_Y = 0.90
LOSS_X = 0.99

is_running = True


#
# Component declarations
#
class Position(Component):
    """Define the position of an entity in the world.

    Position consists in two float: x and y.

    """
    pass


class Speed(Component):
    """Define the speed of an entity in the world.

    Speed consists in two float: x and y.

    """
    pass


class Coordinate(Component):
    """Define coordinates of an entity on the screen.

    Coordinate consists in two float: x and y.

    """
    pass


class Look(Component):
    """Define the look of an entity

    Look consists in three values:

    - image: a Pygame Surface
    - width: the image width
    - height: the image height

    Two last values can also being find using image.get_width|height().

    """
    pass


class Selected(Component):
    """Define if an event has been selected."""
    pass


#
# Event declarations
#
class SelectEntity(Event):
    """An event to select an entity (with a position component)"""
    def call(self, click_position):
        for entity in self.manager.entities_by_type(Position):
            position = entity.get_component(Position).value

            x = position['x'] - RADIUS
            y = position['y'] - RADIUS
            width = RADIUS * 2
            height = RADIUS * 2
            rect = pygame.Rect((x, y, width, height))

            if rect.collidepoint(click_position):
                entity.add_component(Selected())


class UnselectEntity(Event):
    """An event to unselect an entity."""
    def call(self, click_position):
        # Note we should use a list here because we are removing Selected
        # component while iterating on it!
        for entity in list(self.manager.entities_by_type(Selected)):
            entity.del_component(Selected)


#
# Processor (or System) declarations
#
class Input(Processor):
    """Handle input systems (mouse and keyboard)."""
    def __init__(self, screen_size):
        Processor.__init__(self)
        self.screen_width, self.screen_height = screen_size

    def update(self, delta):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                global is_running
                is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                pos = pygame.mouse.get_pos()
                create_ball(self.manager, {
                    'x': pos[0],
                    'y': self.screen_height - pos[1]
                })
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                y = self.screen_height - y
                self.publish(SelectEntity, (x, y))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                x, y = pygame.mouse.get_pos()
                y = self.screen_height - y
                self.publish(UnselectEntity, (x, y))


class Physic(EntityProcessor):
    """Handle physic in the world (considering gravity and world limits)."""

    def __init__(self, screen_size):
        EntityProcessor.__init__(self)
        self.screen_width, self.screen_height = screen_size
        # Note this processor only need Position and Speed so we ask for
        # entities which contain these components. In this demo, there are only
        # balls so all the entities are returned each time.
        self.needed = [Position, Speed]

    def update_entity(self, delta, entity):
        selected = entity.get_component(Selected) is not None

        # We use two behaviour for physic if the entity is selected or not.
        if selected:
            self.update_entity_mouse(delta, entity)
        else:
            self.update_entity_gravity(delta, entity)

        self.update_entity_position(delta, entity)

    def update_entity_mouse(self, delta, entity):
        speed = entity.get_component(Speed)
        position = entity.get_component(Position).value

        click_x, click_y = pygame.mouse.get_pos()
        click_y = self.screen_height - click_y

        speed.value = {
            'x': (click_x - position['x']) * 3,
            'y': (click_y - position['y']) * 3,
        }

    def update_entity_gravity(self, delta, entity):
        speed = entity.get_component(Speed)
        speed.value['y'] += -GRAVITY * delta

    def update_entity_position(self, delta, entity):
        position = entity.get_component(Position)
        speed = entity.get_component(Speed)

        position.value['x'] += speed.value['x'] * delta
        position.value['y'] += speed.value['y'] * delta

        if position.value['y'] < RADIUS:
            position.value['y'] = RADIUS
            speed.value['y'] = -speed.value['y'] * LOSS_Y

        if position.value['x'] < RADIUS:
            position.value['x'] = RADIUS
            speed.value['x'] = -speed.value['x']

        if position.value['x'] > self.screen_width - RADIUS:
            position.value['x'] = self.screen_width - RADIUS
            speed.value['x'] = -speed.value['x']

        # If the entity is nearly stopped on y axis, it's time to stop it on
        # x axis too.
        if abs(speed.value['y']) <= 2 and position.value['y'] == RADIUS:
            speed.value['x'] = speed.value['x'] * LOSS_X


class Graphic(EntityProcessor):
    """Handle position translation on the screen."""
    def __init__(self, screen_size):
        EntityProcessor.__init__(self)
        self.screen_width, self.screen_height = screen_size
        self.needed = [Position, Coordinate]

    def update_entity(self, delta, entity):
        position = entity.get_component(Position)
        coords = entity.get_component(Coordinate)

        # Only y axis is reversed between position and coordinate systems.
        coords.value['x'] = position.value['x']
        coords.value['y'] = self.screen_height - position.value['y']


class Render(EntityProcessor):
    """Show entities on the screen."""
    def __init__(self, screen):
        EntityProcessor.__init__(self)
        self.screen = screen
        self.needed = [Coordinate, Look]

    def pre_update(self, delta):
        # Before showing balls, we paint the screen in black (paint it black!)
        self.screen.fill((0, 0, 0))

    def update_entity(self, delta, entity):
        # Just find coordinates, the look and show the image on the screen.
        coords = entity.get_component(Coordinate)
        look = entity.get_component(Look)

        width = look.value['width']
        height = look.value['height']
        x = coords.value['x'] - width / 2
        y = coords.value['y'] - height / 2
        rect = pygame.Rect(x, y, width, height)

        self.screen.blit(look.value['image'], rect)

    def post_update(self, delta):
        # And finish by showing the new screen!
        pygame.display.flip()


#
# "Archetype" declaration
# Note there is not this kind of concept in pytity yet.
#
def create_ball(manager, position):
    """This function create a ball in the world.

    A ball is an entity with a position, a speed, coordinates on the screen
    and an appearance (a smiley image!).

    """
    entity = manager.create_entity()

    entity.add_component(Position(position))
    entity.add_component(Speed({
        'x': random.uniform(-500, 500),
        'y': random.uniform(-500, 500)
    }))
    entity.add_component(Coordinate({
        'x': 0,
        'y': 0
    }))

    filename = os.path.join('data', 'face.png')
    image = pygame.image.load(filename).convert_alpha()
    entity.add_component(Look({
        'image': image,
        'width': image.get_width(),
        'height': image.get_height(),
    }))


def main():
    # Init Pygame
    width, height = 800, 600
    pygame.init()
    screen = pygame.display.set_mode((width, height))

    # Create a manager and balls (balls are smiley images)
    manager = Manager()
    number_balls = random.randint(1, 20)
    for i in xrange(number_balls):
        create_ball(manager, {
            'x': random.randint(0, width),
            'y': random.randint(0, height)
        })

    # Add the processors (or systems) to the manager
    Input((width, height)).register_to(manager)
    Physic((width, height)).register_to(manager)
    Graphic((width, height)).register_to(manager)
    Render(screen).register_to(manager)

    # Add the events to the manager
    SelectEntity().register_to(manager)
    UnselectEntity().register_to(manager)

    # And start the big loop!
    clock = pygame.time.Clock()
    while is_running:
        delay = clock.tick(60)
        manager.update(float(delay) / 1000)


if __name__ == '__main__':
    main()
