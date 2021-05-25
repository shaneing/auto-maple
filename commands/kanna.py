"""A collection of all commands that a Kanna can use to interact with the game."""

import config
import time
import math
import utils
from vkeys import press, key_down, key_up


class Move(utils.Command):
    """Moves to a given position using the shortest path based on the current Layout."""

    def __init__(self, x, y, adjust='False', max_steps=15):
        self.name = 'Move'
        self.target = (float(x), float(y))
        self.adjust = utils.validate_boolean(adjust)
        self.max_steps = utils.validate_nonzero_int(max_steps)
        self.counter = 0

    def main(self):
        self.counter = self.max_steps
        path = config.layout.shortest_path(config.player_pos, self.target)
        config.path = path.copy()
        config.path.insert(0, config.player_pos)
        for point in path:
            self._step(point)
        if self.adjust:
            Adjust(*self.target).main()

    @utils.run_if_enabled
    def _step(self, target):
        toggle = True
        local_error = utils.distance(config.player_pos, target)
        global_error = utils.distance(config.player_pos, self.target)
        while config.enabled and \
                self.counter > 0 and \
                local_error > config.move_tolerance and \
                global_error > config.move_tolerance:
            if toggle:
                d_x = target[0] - config.player_pos[0]
                if abs(d_x) > config.move_tolerance / math.sqrt(2):
                    jump = str(utils.bernoulli(0.1))
                    if d_x < 0:
                        Teleport('left', jump=jump).main()
                    else:
                        Teleport('right', jump=jump).main()
                    self.counter -= 1
            else:
                d_y = target[1] - config.player_pos[1]
                if abs(d_y) > config.move_tolerance / math.sqrt(2):
                    jump = str(abs(d_y) > config.move_tolerance)
                    if d_y < 0:
                        Teleport('up', jump=jump).main()
                    else:
                        Teleport('down', jump=jump).main()
                    self.counter -= 1
            local_error = utils.distance(config.player_pos, target)
            global_error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


class Adjust(utils.Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        self.name = 'Adjust'
        self.target = (float(x), float(y))
        self.max_steps = utils.validate_nonzero_int(max_steps)
        self.counter = 0

    def main(self):
        self.counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and self.counter > 0 and error > config.adjust_tolerance:
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                threshold = config.adjust_tolerance / math.sqrt(2)
                if abs(d_x) > threshold:
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold:
                            time.sleep(0.01)
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold:
                            time.sleep(0.01)
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    self.counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > config.adjust_tolerance / math.sqrt(2):
                    if d_y < 0:
                        Teleport('up').main()
                    else:
                        key_down('down')
                        time.sleep(0.05)
                        press('space', 3, down_time=0.1)
                        key_up('down')
                        time.sleep(0.05)
                    self.counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


class Buff(utils.Command):
    """Uses each of Kanna's buffs once. Uses 'Haku Reborn' whenever it is available."""

    def __init__(self):
        self.name = 'Buff'
        self.haku_time = 0
        self.buff_time = 0

    def main(self):
        buffs = ['f1', 'f2', 'f4']
        now = time.time()
        if self.haku_time == 0 or now - self.haku_time > 490:
            press('ctrl', 2)
            self.haku_time = now
        if self.buff_time == 0 or now - self.buff_time > config.buff_cooldown:
            for key in buffs:
                press(key, 3, up_time=0.3)
            self.buff_time = now


class Fall(utils.Command):
    """
    Performs a down-jump and then free-falls until the player exceeds a given distance
    from their starting position.
    """

    def __init__(self, distance=config.move_tolerance/2):
        self.name = 'Fall'
        self.distance = float(distance)

    def main(self):
        start = config.player_pos
        key_down('down')
        time.sleep(0.05)
        counter = 6
        while config.enabled and \
                counter > 0 and \
                utils.distance(start, config.player_pos) < self.distance:
            press('space', 1, down_time=0.1)
            counter -= 1
        key_up('down')
        time.sleep(0.1)


class Walk(utils.Command):
    """Walks in the given direction for a set amount of time."""

    def __init__(self, direction, duration):
        self.name = 'Walk'
        self.direction = utils.validate_horizontal_arrows(direction)
        self.duration = float(duration)

    def main(self):
        key_down(self.direction)
        time.sleep(self.duration)
        key_up(self.direction)
        time.sleep(0.05)


class Goto(utils.Command):
    """Moves config.seq_index to the index of the specified label."""

    def __init__(self, label):
        self.name = 'Goto'
        self.label = str(label)

    def main(self):
        try:
            config.seq_index = config.sequence.index(self.label)
        except ValueError:
            print(f"Label '{self.label}' does not exist.")


class Wait(utils.Command):
    """Waits for a set amount of time."""

    def __init__(self, duration):
        self.name = 'Wait'
        self.duration = float(duration)

    def main(self):
        time.sleep(self.duration)


class Teleport(utils.Command):
    """
    Teleports in a given direction, jumping if specified. Adds the player's position
    to the current Layout if necessary.
    """

    def __init__(self, direction, jump='False'):
        self.name = 'Teleport'
        self.direction = utils.validate_arrows(direction)
        self.jump = utils.validate_boolean(jump)

    def main(self):
        num_presses = 3
        time.sleep(0.05)
        if self.direction in ['up', 'down']:
            num_presses = 2
        if self.direction != 'up':
            key_down(self.direction)
            time.sleep(0.05)
        if self.jump:
            if self.direction == 'down':
                press('space', 3, down_time=0.1)
            else:
                press('space', 1)
        if self.direction == 'up':
            key_down(self.direction)
            time.sleep(0.05)
        press('e', num_presses)
        key_up(self.direction)
        if config.record_layout:
            config.layout.add(*config.player_pos)


class Shikigami(utils.Command):
    """Attacks using 'Shikigami Haunting' in a given direction."""

    def __init__(self, direction, num_attacks=2, repetitions=1):
        self.name = 'Shikigami'
        self.direction = utils.validate_horizontal_arrows(direction)
        self.num_attacks = int(num_attacks)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(0.05)
        key_down(self.direction)
        time.sleep(0.05)
        for _ in range(self.repetitions):
            press('r', self.num_attacks, up_time=0.05)
        key_up(self.direction)
        time.sleep(0.15)


class Tengu(utils.Command):
    """Uses 'Tengu Strike' once."""

    def __init__(self):
        self.name = 'Tengu'

    def main(self):
        press('q', 1)


class Yaksha(utils.Command):
    """
    Places 'Ghost Yaksha Boss' in a given direction, or towards the center of the map if
    no direction is specified.
    """

    def __init__(self, direction=None):
        self.name = 'Yaksha'
        if direction is None:
            self.direction = direction
        else:
            self.direction = utils.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1, up_time=0.05)
        else:
            if config.player_pos[0] > 0.5:
                press('left', 1, down_time=0.1, up_time=0.05)
            else:
                press('right', 1, down_time=0.1, up_time=0.05)
        press('2', 3)


class Kishin(utils.Command):
    """Uses 'Kishin Shoukan' once."""

    def __init__(self):
        self.name = 'Kishin'

    def main(self):
        press('lshift', 4, down_time=0.1, up_time=0.15)


class NineTails(utils.Command):
    """Uses 'Nine-Tailed Fury' once."""

    def __init__(self):
        self.name = 'NineTails'

    def main(self):
        press('3', 3)


class Exorcist(utils.Command):
    """Uses 'Exorcist's Charm' once."""

    def __init__(self):
        self.name = 'Exorcist'

    def main(self):
        press('w', 1, down_time=0.15)


class Domain(utils.Command):
    """Uses 'Spirit's Domain' once."""

    def __init__(self):
        self.name = 'Domain'

    def main(self):
        press('v', 3)


class Legion(utils.Command):
    """Uses 'Ghost Yaksha: Great Oni Lord's Legion' once."""

    def __init__(self):
        self.name = 'Legion'

    def main(self):
        press('z', 2, down_time=0.1)
