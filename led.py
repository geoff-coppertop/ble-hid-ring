from board import LED_RED, LED_GREEN, LED_BLUE
from digitalio import DigitalInOut
from enum import Enum

import asyncio


class Colour(Enum):
    OFF = None
    RED = None
    GREEN = None
    BLUE = None
    ORANGE = None
    PURPLE = None
    WHITE = None

    def __init__(self, red: bool, green: bool, blue: bool):
        self.__red = red
        self.__green = green
        self.__blue = blue

    def __str__(self) -> str:
        return f"{super().__str__()}, R: {self.red}, G: {self.green}, B: {self.blue}"

    def __repr__(self) -> str:
        return f"{super().__repr__()}, R: {self.red}, G: {self.green}, B: {self.blue}"

    @property
    def red(self) -> bool:
        return self.__red

    @property
    def green(self) -> bool:
        return self.__green

    @property
    def blue(self) -> bool:
        return self.__blue


Colour.OFF = Colour(False, False, False)
Colour.RED = Colour(True, False, False)
Colour.GREEN = Colour(False, True, False)
Colour.BLUE = Colour(False, False, True)
Colour.ORANGE = Colour(True, True, False)
Colour.PURPLE = Colour(True, False, True)
Colour.WHITE = Colour(True, True, True)


class LEDState(Enum):
    OFF = None
    RED_BLINK = None
    RED_SOLID = None
    GREEN_BLINK = None
    GREEN_SOLID = None
    BLUE_BLINK = None
    BLUE_SOLID = None
    ORANGE_BLINK = None
    ORANGE_SOLID = None
    PURPLE_BLINK = None
    PURPLE_SOLID = None
    WHITE_BLINK = None
    WHITE_SOLID = None

    RED_GREEN_BLINK = None
    RED_BLUE_BLINK = None
    RED_ORANGE_BLINK = None
    RED_PURPLE_BLINK = None
    RED_WHITE_BLINK = None
    GREEN_BLUE_BLINK = None
    GREEN_ORANGE_BLINK = None
    GREEN_PURPLE_BLINK = None
    GREEN_WHITE_BLINK = None
    BLUE_ORANGE_BLINK = None
    BLUE_PURPLE_BLINK = None
    BLUE_WHITE_BLINK = None
    ORANGE_PURPLE_BLINK = None
    ORANGE_WHITE_BLINK = None
    PURPLE_WHITE_BLINK = None

    def __init__(self, primary: Colour, secondary: Colour):
        self.__primary = primary
        self.__secondary = secondary

    def __repr__(self) -> str:
        return f"{super().__repr__()}\n\tPri: {self.primary}\n\tSec: {self.secondary}"

    def __str__(self) -> str:
        return f"{super().__str__()}\n\tPri: {self.primary}\n\tSec: {self.secondary}"

    @property
    def primary(self) -> Colour:
        return self.__primary

    @property
    def secondary(self) -> Colour:
        return self.__secondary


LEDState.OFF = LEDState(Colour.OFF, Colour.OFF)

LEDState.RED_BLINK = LEDState(Colour.RED, Colour.OFF)
LEDState.RED_SOLID = LEDState(Colour.RED, Colour.RED)
LEDState.RED_GREEN_BLINK = LEDState(Colour.RED, Colour.GREEN)
LEDState.RED_BLUE_BLINK = LEDState(Colour.RED, Colour.BLUE)
LEDState.RED_ORANGE_BLINK = LEDState(Colour.RED, Colour.ORANGE)
LEDState.RED_PURPLE_BLINK = LEDState(Colour.RED, Colour.PURPLE)
LEDState.RED_WHITE_BLINK = LEDState(Colour.RED, Colour.WHITE)

LEDState.GREEN_BLINK = LEDState(Colour.GREEN, Colour.OFF)
LEDState.GREEN_SOLID = LEDState(Colour.GREEN, Colour.GREEN)
LEDState.GREEN_BLUE_BLINK = LEDState(Colour.GREEN, Colour.BLUE)
LEDState.GREEN_ORANGE_BLINK = LEDState(Colour.GREEN, Colour.ORANGE)
LEDState.GREEN_PURPLE_BLINK = LEDState(Colour.GREEN, Colour.PURPLE)
LEDState.GREEN_WHITE_BLINK = LEDState(Colour.GREEN, Colour.WHITE)

LEDState.BLUE_BLINK = LEDState(Colour.BLUE, Colour.OFF)
LEDState.BLUE_SOLID = LEDState(Colour.BLUE, Colour.BLUE)
LEDState.BLUE_ORANGE_BLINK = LEDState(Colour.BLUE, Colour.ORANGE)
LEDState.BLUE_PURPLE_BLINK = LEDState(Colour.BLUE, Colour.PURPLE)
LEDState.BLUE_WHITE_BLINK = LEDState(Colour.BLUE, Colour.WHITE)

LEDState.ORANGE_BLINK = LEDState(Colour.ORANGE, Colour.OFF)
LEDState.ORANGE_SOLID = LEDState(Colour.ORANGE, Colour.ORANGE)
LEDState.ORANGE_PURPLE_BLINK = LEDState(Colour.ORANGE, Colour.PURPLE)
LEDState.ORANGE_WHITE_BLINK = LEDState(Colour.ORANGE, Colour.WHITE)

LEDState.PURPLE_BLINK = LEDState(Colour.PURPLE, Colour.OFF)
LEDState.PURPLE_SOLID = LEDState(Colour.PURPLE, Colour.PURPLE)
LEDState.PURPLE_WHITE_BLINK = LEDState(Colour.PURPLE, Colour.WHITE)

LEDState.WHITE_BLINK = LEDState(Colour.WHITE, Colour.OFF)
LEDState.WHITE_SOLID = LEDState(Colour.WHITE, Colour.WHITE)

class LEDCommunicator:
    def __init__(self):
        self.__current = LEDState.OFF
        self.__next = LEDState.OFF

    @property
    def next_pattern(self, value):
        if value is self.__current:
            return

        self.__next = value

    @property
    def async task(self):
        with DigitalInOut(LED_RED) as led_red, DigitalInOut(
            LED_GREEN
        ) as led_green, DigitalInOut(LED_BLUE) as led_blue:
            led_red.switch_to_output(value=False)
            led_green.switch_to_output(value=False)
            led_blue.switch_to_output(value=False)

            update_from_next = False

            while True:
                update_from_next ^= True

                if update_from_next and (self.__next is not self.__current):
                    self.__current = self.__next

                    # print(f"Updating LED state: {self.__current}")

                    current_colour = self.__current.primary
                    next_colour = self.__current.secondary

                # print(f"Current colour: {current_colour}")
                # print(f"Next colour: {next_colour}")

                led_red.value = not current_colour.red
                led_green.value = not current_colour.green
                led_blue.value = not current_colour.blue

                await asyncio.sleep(0.5)

                # Set the current colour
                temp_colour = current_colour
                current_colour = next_colour
                next_colour = temp_colour
