import asyncio

from enum import Enum
from board import D0, D1, D2, D3
from data_producer import DataProducer
from keypad import Keys


class Button(Enum):
    LEFT = None
    RIGHT = None
    UP = None
    DOWN = None

    def __init__(self, pin):
        self.pin = pin


Button.LEFT = Button(D0)
Button.RIGHT = Button(D3)
Button.UP = Button(D2)
Button.DOWN = Button(D1)


class ButtonMonitor(DataProducer):
    """Watches buttons"""

    BUTTONS = [
        Button.LEFT,
        Button.RIGHT,
        Button.UP,
        Button.DOWN,
    ]

    BUTTON_PINS = [button.pin for button in BUTTONS]

    def __init__(self):
        super().__init__()

        self.__pressed = []
        self.__released = [
            Button.LEFT,
            Button.RIGHT,
            Button.UP,
            Button.DOWN,
        ]

    @property
    def pressed(self):
        return self.__pressed

    def __press(self, button: Button):
        if button not in self.__released:
            return

        self.__released.remove(button)
        self.__pressed.append(button)

        print(f"{button} pressed")

        self.notify_callbacks()

    def __release(self, button: Button):
        if button not in self.__pressed:
            return

        self.__pressed.remove(button)
        self.__released.append(button)

        print(f"{button} released")

        self.notify_callbacks()

    @property
    async def task(self):
        with Keys(
            ButtonMonitor.BUTTON_PINS, value_when_pressed=False, pull=True
        ) as buttons:
            while True:
                event = buttons.events.get()

                if event:
                    button_number = event.key_number
                    # A key transition occurred.
                    if event.pressed:
                        self.__press(ButtonMonitor.BUTTONS[button_number])

                    if event.released:
                        self.__release(ButtonMonitor.BUTTONS[button_number])

                await asyncio.sleep(0)
