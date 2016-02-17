# coding: utf-8

import os
import random
import sys
sys.path.insert(1, '..')

import pygame
pygame.init()

from pytity import Manager


WIN_SCORE = 5

SCREEN = pygame.display.set_mode()
SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN.get_width(), SCREEN.get_height()
pygame.display.toggle_fullscreen()

FONT_FILENAME = os.path.join('data', 'OpenSans-Bold.ttf')
FONT = pygame.font.Font(FONT_FILENAME, 50)

BACKGROUND_COLOR = (0, 0, 0)

is_running = True
game_speed = 1


#
# Processors
#
def user_interaction(manager, delta):
    global is_running
    global game_speed
    playable_entities = manager.entities_by_types(['playable', 'position'])
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            is_running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            game_speed += 0.5
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            game_speed -= 0.5
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            manager.publish({
                'type': 'NEW_BALL'
            })
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            manager.publish({
                'type': 'NEW_GAME'
            })
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            for entity in playable_entities:
                keys_actions = manager.get_component(entity, 'playable')
                if event.type == pygame.KEYUP and (event.key == keys_actions['down'] or event.key == keys_actions['up']):
                    manager.publish({
                        'type': 'ENTITY_STOP_MOVEMENT',
                        'entity': entity,
                    })
                elif event.type == pygame.KEYDOWN and event.key == keys_actions['down']:
                    manager.publish({
                        'type': 'ENTITY_DOWN_MOVEMENT',
                        'entity': entity,
                    })
                elif event.type == pygame.KEYDOWN and event.key == keys_actions['up']:
                    manager.publish({
                        'type': 'ENTITY_UP_MOVEMENT',
                        'entity': entity,
                    })


def ia_interaction(manager, delta):
    for entity in manager.entities_by_types(['ia', 'position', 'size']):
        ia = manager.get_component(entity, 'ia')
        position = manager.get_component(entity, 'position')
        size = manager.get_component(entity, 'size')
        position_observe = manager.get_component(ia['observe'], 'position')

        if position['y'] + size['height']/5 > position_observe['y'] > position['y'] - size['height']/5:
            manager.publish({
                'type': 'ENTITY_STOP_MOVEMENT',
                'entity': entity,
            })
        elif position_observe['y'] < position['y'] - size['height']/3:
            manager.publish({
                'type': 'ENTITY_DOWN_MOVEMENT',
                'entity': entity,
            })
        elif position_observe['y'] > position['y'] + size['height']/3:
            manager.publish({
                'type': 'ENTITY_UP_MOVEMENT',
                'entity': entity,
            })


def physic(manager, delta):
    def collide(pos1, pos2):
        ball_rect = pygame.Rect(pos1['x'] - 5, pos1['y'] - 5, 10, 10)
        player_rect = pygame.Rect(pos2['x'] - 5, pos2['y'] - 50, 10, 100)
        return ball_rect.colliderect(player_rect)

    player1, player2 = None, None
    for entity in manager.entities_by_types(['position', 'speed', 'side']):
        if manager.get_component(entity, 'side') == 'left':
            player1 = entity
        else:
            player2 = entity

    if player1 is not None and player2 is not None:
        player1_position = manager.get_component(player1, 'position')
        player2_position = manager.get_component(player2, 'position')
        player1_speed = manager.get_component(player1, 'speed')
        player2_speed = manager.get_component(player2, 'speed')

    for entity in manager.entities_by_types(['position', 'speed']):
        position = manager.get_component(entity, 'position')
        speed = manager.get_component(entity, 'speed')

        next_position = {
            'x': position['x'],
            'y': position['y']
        }
        next_speed_x, next_speed_y = speed['x'], speed['y']

        next_position['x'] += speed['x'] * delta
        next_position['y'] += speed['y'] * delta

        if next_position['y'] < 0:
            next_position['y'] = 0
            next_speed_y = -speed['y']

        if next_position['y'] > SCREEN_HEIGHT:
            next_position['y'] = SCREEN_HEIGHT
            next_speed_y = -speed['y']

        if player1 is not None and entity != player1 and collide(next_position, player1_position):
            next_position['x'] = player1_position['x'] + 10
            next_speed_x = -speed['x']
            next_speed_y += player1_speed['y']

        if player2 is not None and entity != player2 and collide(next_position, player2_position):
            next_position['x'] = player2_position['x'] - 10
            next_speed_x = -speed['x']
            next_speed_y += player2_speed['y']

        if next_position['x'] < 0:
            next_position['x'] = 0
            next_speed_x = -speed['x']

        if next_position['x'] > SCREEN_WIDTH:
            next_position['x'] = SCREEN_WIDTH
            next_speed_x = -speed['x']

        manager.publish({
            'type': 'ENTITY_MOVEMENT',
            'entity': entity,
            'position': next_position,
            'speed': {
                'x': next_speed_x,
                'y': next_speed_y
            },
        })


def score_monitor(manager, delta):
    scoring = {
        'left': 0,
        'right': 0,
    }
    for entity in manager.entities_by_types(['position', 'increase_score']):
        position = manager.get_component(entity, 'position')
        if position['x'] <= 0:
            scoring['right'] += 1
        elif position['x'] >= SCREEN_WIDTH:
            scoring['left'] += 1

    for entity in manager.entities_by_types(['side', 'score']):
        side = manager.get_component(entity, 'side')
        score = manager.get_component(entity, 'score')

        if scoring[side] > 0:
            score += scoring[side]
            manager.publish({
                'type': 'GOAL',
                'entity': entity,
                'score': score,
            })

        if score >= WIN_SCORE:
            manager.publish({
                'type': 'WINNER',
                'entity': entity,
            })


def rendering(manager, delta):
    SCREEN.fill(BACKGROUND_COLOR)
    for entity in manager.entities_by_types(['position', 'size']):
        position = manager.get_component(entity, 'position')
        size = manager.get_component(entity, 'size')
        coords = {
            'x': position['x'],
            'y': SCREEN_HEIGHT - position['y'],
        }
        color = manager.get_component(entity, 'color')
        if color is None:
            color = (255, 255, 255)

        x = coords['x'] - size['width'] / 2
        y = coords['y'] - size['height'] / 2
        rect = pygame.Rect(x, y, size['width'], size['height'])
        pygame.draw.rect(SCREEN, color, rect)

    for entity in manager.entities_by_types(['score', 'side']):
        score = manager.get_component(entity, 'score')
        side = manager.get_component(entity, 'side')
        color = manager.get_component(entity, 'color')
        if color is None:
            color = (255, 255, 255)

        surface = FONT.render(str(score), True, color)
        width = surface.get_width()
        height = surface.get_height()
        if side == 'left':
            x = 200
        else:
            x = SCREEN_WIDTH - 200 - width

        SCREEN.blit(surface, (x, 10, width, height))

    for entity in manager.entities_by_type('label'):
        label = manager.get_component(entity, 'label')
        color = manager.get_component(entity, 'color')
        if color is None:
            color = (255, 255, 255)

        surface = FONT.render(label, True, color)
        width = surface.get_width()
        height = surface.get_height()
        x = (SCREEN_WIDTH - width) / 2
        y = (SCREEN_HEIGHT - height) / 2

        SCREEN.blit(surface, (x, y, width, height))

    pygame.display.flip()


#
# Mutators
#
def score_up(manager, action):
    entity = action['entity']
    score = action['score']
    manager.set_component(entity, 'score', score)


def entity_mutator(manager, action):
    type_ = action['type']
    entity = action['entity']
    if type_ == 'ENTITY_MOVEMENT':
        manager.set_component(entity, 'position', action['position'])
        manager.set_component(entity, 'speed', action['speed'])
    elif type_ == 'ENTITY_UP_MOVEMENT':
        manager.set_component(entity, 'speed', {
            'x': 0,
            'y': 100
        })
    elif type_ == 'ENTITY_DOWN_MOVEMENT':
        manager.set_component(entity, 'speed', {
            'x': 0,
            'y': -100
        })
    elif type_ == 'ENTITY_STOP_MOVEMENT':
        manager.set_component(entity, 'speed', {
            'x': 0,
            'y': 0
        })


def new_winner(manager, action):
    winner_name = manager.get_component(action['entity'], 'name')
    color = manager.get_component(action['entity'], 'color')

    for entity in list(manager.entities()):
        manager.kill_entity(entity)

    winner_label = manager.create_entity({
        'label': '%s won the game!' % winner_name,
        'color': color,
    })


def new_game(manager, action):
    load_play_scene(manager)


def new_ball(manager, action):
    manager.create_entity(ball_schema())


#
# Schemas creators
#
def ball_schema():
    speed = {
        'x': 200 if random.choice((True, False)) else -200,
        'y': random.randint(-100, 100)
    }

    return {
        'color': (255, 255, 255),
        'size': {
            'width': 10,
            'height': 10,
        },
        'position': {
            'x': SCREEN_WIDTH / 2,
            'y': random.randint(0, SCREEN_HEIGHT),
        },
        'speed': speed,
        'increase_score': True,
    }


def player_schema(side):
    global number_players
    number_players += 1
    return {
        'name': 'Player %d' % number_players,
        'score': 0,
        'side': side,
        'color': [random.randint(100, 255) for i in range(3)],
        'size': {
            'width': 10,
            'height': 100,
        },
        'position': {
            'x': 50 if side == 'left' else SCREEN_WIDTH - 50,
            'y': SCREEN_HEIGHT / 2,
        },
        'speed': {
            'x': 0,
            'y': 0
        }
    }


def wall_schema(rect):
    return {
        'position': {
            'x': rect[0],
            'y': rect[1],
        },
        'size': {
            'width': rect[2],
            'height': rect[3],
        },
        'color': (50, 50, 50),
    }

#
# Scenes
#
def load_play_scene(manager):
    global number_players
    number_players = 0

    for entity in list(manager.entities()):
        manager.kill_entity(entity)
    manager.actions_waiting_store.clear()

    ball = manager.create_entity(ball_schema())
    player1 = manager.create_entity(player_schema('left'))
    manager.set_component(player1, 'playable', {
        'up': pygame.K_UP,
        'down': pygame.K_DOWN,
    })
    player2 = manager.create_entity(player_schema('right'))
    manager.set_component(player2, 'ia', {
        'observe': ball,
    })

    manager.create_entity(wall_schema((0, SCREEN_HEIGHT/2, 5, SCREEN_HEIGHT)))
    manager.create_entity(wall_schema((SCREEN_WIDTH/2, 0, SCREEN_WIDTH, 5)))
    manager.create_entity(wall_schema((SCREEN_WIDTH, SCREEN_HEIGHT/2, 5, SCREEN_HEIGHT)))
    manager.create_entity(wall_schema((SCREEN_WIDTH/2, SCREEN_HEIGHT, SCREEN_WIDTH, 5)))

if __name__ == '__main__':
    manager = Manager()

    load_play_scene(manager)

    manager.register_processor(physic)
    manager.register_processor(user_interaction)
    manager.register_processor(ia_interaction)
    manager.register_processor(score_monitor)
    manager.register_processor(rendering)

    manager.register_mutator_on('ENTITY_MOVEMENT', entity_mutator)
    manager.register_mutator_on('ENTITY_UP_MOVEMENT', entity_mutator)
    manager.register_mutator_on('ENTITY_DOWN_MOVEMENT', entity_mutator)
    manager.register_mutator_on('ENTITY_STOP_MOVEMENT', entity_mutator)
    manager.register_mutator_on('GOAL', score_up)
    manager.register_mutator_on('WINNER', new_winner)
    manager.register_mutator_on('NEW_GAME', new_game)
    manager.register_mutator_on('NEW_BALL', new_ball)

    clock = pygame.time.Clock()
    while is_running:
        delay = clock.tick(60)
        manager.update(float(delay) * game_speed / 1000)
        manager.mutate()
