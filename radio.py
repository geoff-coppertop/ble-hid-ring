import asyncio
import time

from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard import BatteryService
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService

from enum import Enum
from data_producer import DataProducer


class RadioState(Enum):
    """Radio State Enumeration"""

    STARTING_ADVERTISING = None
    ADVERTISING = None
    CONNECTED = None
    TURNING_OFF = None
    STOPPING = None


RadioState.STARTING_ADVERTISING = RadioState()
RadioState.ADVERTISING = RadioState()
RadioState.CONNECTED = RadioState()
RadioState.TURNING_OFF = RadioState()
RadioState.OFF = RadioState()


class Radio(DataProducer):
    """Defines radio interaction"""

    def __init__(self):
        super().__init__()

        self.__state = RadioState.OFF
        self.__battery = BatteryService()
        self.__hid = HIDService()
        self.__event = asyncio.Event()

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        if value is self.state:
            return

        self.__state = value

        print(f"Radio state: {self.state}")

        self.notify_callbacks()

    @property
    def hid_service(self):
        return self.__hid

    @property
    def battery_service(self):
        return self.__battery

    def start(self):
        if self.state not in [RadioState.OFF, RadioState.TURNING_OFF]:
            return FALSE

        self.state = RadioState.STARTING_ADVERTISING
        self.__event.set()

        return TRUE

    def stop(self):
        if self.state in [RadioState.OFF, RadioState.TURNING_OFF]:
            return FALSE

        self.state = RadioState.STOPPING
        self.__event.set()

        return TRUE

    async def __event_wait(self, timeout=None):
        try:
            await asyncio.wait_for(self.__event.wait(), timeout)
        except asyncio.TimeoutError as err:
            return False

        self.__event.clear()

        return True

    async def __sleep(
        self,
        radio: BLERadio,
    ) -> None:
        self.state = RadioState.OFF

        for connection in radio.connections:
            connection.disconnect()

        radio.stop_advertising()

        await self.__event_wait()

    async def __advertise(
        self,
        radio: BLERadio,
    ) -> bool:
        self.state = RadioState.ADVERTISING

        # device_info = DeviceInfoService(software_revision=1)

        advertisement = ProvideServicesAdvertisement(self.__hid, self.__battery)

        scan_response = Advertisement()
        scan_response.short_name = "HID Ring"
        scan_response.complete_name = "HID Ring"

        radio.start_advertising(advertisement)

        start = time.monotonic()

        ret_val = True

        while not radio.connected:
            if time.monotonic() - start >= 10:
                ret_val = False
                break

            if not await self.__event_wait(0.25):
                ret_val = False
                break

        radio.stop_advertising()

        return ret_val

    async def __monitor_connection(
        self,
        radio: BLERadio,
    ) -> None:
        self.state = RadioState.CONNECTED

        while radio.connected:
            if not await self.__event_wait(0.25):
                continue

            break

        if self.state is RadioState.TURNING_OFF:
            return

        self.__event.set()

    @property
    async def task(self):
        radio = BLERadio()

        radio.name = "HID Ring"

        while True:
            await self.__sleep(radio)

            if not await self.__advertise(radio):
                # No connection formed during advertising, go back to sleep
                continue

            await self.__monitor_connection(radio)
