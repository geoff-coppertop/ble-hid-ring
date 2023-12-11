import asyncio

from button import Button
from data_producer import DataProducer
from enum import Enum


class SystemState(Enum):
    """"""

    SLEEP
    ACTIVE_BUTTONS
    ACTIVE_IMU


SystemState.SLEEP = SystemState()
SystemState.ACTIVE = SystemState()


class SystemController:
    BUTTON_COMBO_IMU_TOGGLE = {Button.DOWN, Button.Left}
    BUTTON_COMBO_POWER_OFF = {Button.UP, Button.Left}

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
                self.handle_sleep()

            elif self.__state is SystemState.ACTIVE:
                self.handle_active()

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
        if len(button.pressed) > 0:
            self.__radio.start()

    def active_buttons_entry(self):
        self.__imu.stop()
        self.__radio.start()

    def active_buttons_handler(self):
        if self.__radio.state is RadioState.OFF:
            return SystemState.SLEEP

        elif radio.state is RadioState.ADVERTISING:
            if battery.state is BatteryState.CHARGING:
                state.led = LEDState.GREEN_BLUE_BLINK
            elif battery.state is BatteryState.LOW:
                state.led = LEDState.RED_BLUE_BLINK
            else:
                state.led = LEDState.BLUE_BLINK

        else:
            if battery.state is BatteryState.CHARGING:
                state.led = LEDState.GREEN_BLINK
            elif battery.state is BatteryState.LOW:
                state.led = LEDState.RED_BLINK
            else:
                state.led = LEDState.OFF

    def active_imu_entry(self):
        self.__imu.start()
        self.__radio.start()

    def active_imu_handler(self):
        if self.__radio.state is RadioState.OFF:
            return SystemState.SLEEP

        elif radio.state is RadioState.ADVERTISING:
            if battery.state is BatteryState.CHARGING:
                state.led = LEDState.GREEN_PURPLE_BLINK
            elif battery.state is BatteryState.LOW:
                state.led = LEDState.RED_PURPLE_BLINK
            else:
                state.led = LEDState.PURPLE_BLINK

        else:
            if battery.state is BatteryState.CHARGING:
                state.led = LEDState.GREEN_BLINK
            elif battery.state is BatteryState.LOW:
                state.led = LEDState.RED_BLINK
            else:
                state.led = LEDState.OFF
