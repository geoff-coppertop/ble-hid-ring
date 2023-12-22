import asyncio

from button import Button
from data_producer import DataProducer
from enum import Enum
from radio import RadioState
from battery import BatteryState
from led import LEDState


class SystemState(Enum):
    """System State Enumeration"""

    SLEEP = None
    ACTIVE = None
    ACTIVE_BUTTONS = None
    ACTIVE_IMU = None


SystemState.SLEEP = SystemState()
SystemState.ACTIVE = SystemState()
SystemState.ACTIVE_BUTTONS = SystemState()
SystemState.ACTIVE_IMU = SystemState()


class SystemController:
    BUTTON_COMBO_IMU_TOGGLE = {Button.DOWN, Button.LEFT}
    BUTTON_COMBO_POWER_OFF = {Button.UP, Button.LEFT}

    def __init__(self, battery, button, imu, led, radio):
        self.__state = SystemState.SLEEP
        self.__imu_toggle_armed = False
        self.__imu_toggle_time = None

        self.__battery = battery
        self.__button = button
        self.__imu = imu
        self.__led = led
        self.__radio = radio

        self.__event = asyncio.Event()

        for component in [battery, button, imu, led, radio]:
            if isinstance(component, DataProducer):
                component.register_callback(self.update)

    def update(self):
        self.__event.set()

    @property
    async def task(self):
        while True:
            if self.__state is SystemState.SLEEP:
                self.sleep_handler()

            elif self.__state is SystemState.ACTIVE:
                self.active_handler()

            await self.__event_wait()

    async def __event_wait(self, timeout=None):
        try:
            await asyncio.wait_for(self.__event.wait(), timeout)
        except asyncio.TimeoutError as err:
            return False

        self.__event.clear()

        return True

    def sleep_entry(self):
        self.__imu.stop()
        self.__radio.stop()

    def sleep_handler(self):
        if len(self.__button.pressed) > 0:
            self.__radio.start()

    # not sure this is the intent, just put it here so it runs
    def active_handler(self):
        self.active_buttons_handler()
        self.active_imu_handler()

    def active_buttons_entry(self):
        self.__imu.stop()
        self.__radio.start()

    def active_buttons_handler(self):
        if self.__radio.state is RadioState.OFF:
            return SystemState.SLEEP

        elif self.__radio.state is RadioState.ADVERTISING:
            if self.__battery.state is BatteryState.CHARGING:
                self.__state.led = LEDState.GREEN_BLUE_BLINK
            elif self.__battery.state is BatteryState.LOW:
                self.__state.led = LEDState.RED_BLUE_BLINK
            else:
                self.__state.led = LEDState.BLUE_BLINK

        else:
            if self.__battery.state is BatteryState.CHARGING:
                self.__state.led = LEDState.GREEN_BLINK
            elif self.__battery.state is BatteryState.LOW:
                self.__state.led = LEDState.RED_BLINK
            else:
                self.__state.led = LEDState.OFF

    def active_imu_entry(self):
        self.__imu.start()
        self.__radio.start()

    def active_imu_handler(self):
        if self.__radio.state is RadioState.OFF:
            return SystemState.SLEEP

        elif self.__radio.state is RadioState.ADVERTISING:
            if self.__battery.state is BatteryState.CHARGING:
                self.__state.led = LEDState.GREEN_PURPLE_BLINK
            elif self.__battery.state is BatteryState.LOW:
                self.__state.led = LEDState.RED_PURPLE_BLINK
            else:
                self.__state.led = LEDState.PURPLE_BLINK

        else:
            if self.__battery.state is BatteryState.CHARGING:
                self.__state.led = LEDState.GREEN_BLINK
            elif self.__battery.state is BatteryState.LOW:
                self.__state.led = LEDState.RED_BLINK
            else:
                self.__state.led = LEDState.OFF
