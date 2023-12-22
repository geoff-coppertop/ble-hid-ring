import asyncio

from data_producer import DataProducer
from enum import Enum
from seeed_xiao_nrf52840 import Battery


class BatteryState(Enum):
    """Battery State Enumeration"""

    OK = None
    LOW = None
    CHARGING = None


BatteryState.OK = BatteryState()
BatteryState.LOW = BatteryState()
BatteryState.CHARGING = BatteryState()


class BatteryUpdateRate(Enum):
    """Battery Update Rate Enumeration"""

    SLOW = None
    FAST = None


BatteryUpdateRate.SLOW = BatteryUpdateRate()
BatteryUpdateRate.FAST = BatteryUpdateRate()


class BatteryMonitor(DataProducer):
    """Watches the battery"""

    def __init__(self):
        super().__init__()

        self.__state = BatteryState.OK

        with Battery() as battery:
            self.__level = battery.voltage

        self.sample_battery()

        self.__rate = BatteryUpdateRate.SLOW

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        if value is self.__state:
            return

        self.__state = value

        print(f"Battery state: {self.state}")

        self.notify_callbacks()

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, value):
        self.__level *= 0.9
        self.__level += 0.1 * value

        print(f"Battery level: {self.level}")

    @property
    def rate(self):
        return self.__rate

    @rate.setter
    def rate(self, value):
        if value == self.__rate:
            return

        self.__rate = value
        print(f"Battery update rate: {self.rate}")

    @property
    async def task(self):
        while True:
            self.sample_battery()

            if self.rate is BatteryUpdateRate.SLOW:
                await asyncio.sleep(120)
            elif self.rate is BatteryUpdateRate.FAST:
                await asyncio.sleep(20)
            else:
                raise ValueError(f"Invalid BatteryUpdateRate")

    def sample_battery(self):
        with Battery() as battery:
            self.level = battery.voltage

            state = BatteryState.OK

            if not battery.charge_status:
                state = BatteryState.CHARGING

            elif self.level <= 3.6:
                state = BatteryState.LOW

            self.state = state
