# -*- coding: utf-8 -*-

"""
This demo shows a simple example to show how to use pytity in your project.
It is highly based on libes demo, another entity system library (in C++). All
the credits go to its author!

https://github.com/jube/libes

"""

import sys
sys.path.insert(1, '..')

import os
import random

import pygame
pygame.init()

from pytity import Manager


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

GRAVITY = 200
RADIUS = 24
LOSS_Y = 0.90
LOSS_X = 0.99

IMAGE_FILENAME = os.path.join('data', 'face.png')
IMAGE = pygame.image.load(IMAGE_FILENAME).convert_alpha()

is_running = True


def user_interaction(manager, delta):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            global is_running
            is_running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            manager.publish({
                'type': 'CREATE_SMILEY',
                'position': {
                    'x': pos[0],
                    'y': SCREEN_HEIGHT - pos[1]
                }
            })

def physic(manager, delta):
    for smiley in manager.entities_by_types(['position', 'speed']):
        position = manager.get_component(smiley, 'position')
        speed = manager.get_component(smiley, 'speed')

        next_position_x, next_position_y = position['x'], position['y']
        next_speed_x, next_speed_y = speed['x'], speed['y']

        next_speed_y += -GRAVITY * delta
        next_position_x += speed['x'] * delta
        next_position_y += speed['y'] * delta

        if next_position_y < RADIUS:
            next_position_y = RADIUS
            next_speed_y = -speed['y'] * LOSS_Y

        if next_position_x < RADIUS:
            next_position_x = RADIUS
            next_speed_x = -speed['x']

        if next_position_x > SCREEN_WIDTH - RADIUS:
            next_position_x = SCREEN_WIDTH - RADIUS
            next_speed_x = -speed['x']

        manager.publish({
            'type': 'SMILEY_MOVEMENT',
            'smiley': smiley,
            'position': {
                'x': next_position_x,
                'y': next_position_y
            },
            'speed': {
                'x': next_speed_x,
                'y': next_speed_y
            },
        })


def rendering(manager, delta):
    SCREEN.fill((0, 0, 0))
    for smiley in manager.entities_by_types(['position', 'look']):
        position = manager.get_component(smiley, 'position')
        look = manager.get_component(smiley, 'look')
        coords = {
            'x': position['x'],
            'y': SCREEN_HEIGHT - position['y'],
        }

        x = coords['x'] - look['width'] / 2
        y = coords['y'] - look['height'] / 2
        rect = pygame.Rect(x, y, look['width'], look['height'])

        SCREEN.blit(look['image'], rect)

    pygame.display.flip()


def smiley_creator(manager, action):
    smiley = manager.create_entity()

    manager.set_component(smiley, 'position', action['position'])
    manager.set_component(smiley, 'speed', {
        'x': random.uniform(-500, 500),
        'y': random.uniform(-500, 500)
    })
    manager.set_component(smiley, 'look', {
        'image': IMAGE,
        'width': IMAGE.get_width(),
        'height': IMAGE.get_height(),
    })


def smiley_mover(manager, action):
    smiley = action['smiley']
    manager.set_component(smiley, 'position', action['position'])
    manager.set_component(smiley, 'speed', action['speed'])


if __name__ == '__main__':
    # Create a manager and balls (balls are smiley images)
    manager = Manager()

    # Add the processors (or systems) to the manager
    manager.register_processor(user_interaction)
    manager.register_processor(physic)
    manager.register_processor(rendering)

    manager.register_mutator_on('CREATE_SMILEY', smiley_creator)
    manager.register_mutator_on('SMILEY_MOVEMENT', smiley_mover)

    number_smileys = random.randint(1, 20)
    for i in range(number_smileys):
        manager.publish({
            'type': 'CREATE_SMILEY',
            'position': {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT)
            }
        })

    # And start the big loop!
    clock = pygame.time.Clock()
    while is_running:
        delay = clock.tick(60)
        manager.update(float(delay) / 1000)
        manager.mutate()
