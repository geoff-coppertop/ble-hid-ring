import asyncio


from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard import BatteryService
from adafruit_ble.services.standard.hid import HIDService

# from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_lsm6ds.lsm6ds3 import LSM6DS3

from board import LED_RED, LED_GREEN, LED_BLUE, D0, D1, D2, D3
from digitalio import DigitalInOut
from keypad import Keys
from seeed_xiao_nrf52840 import Battery, IMU


class Button:
    LEFT = None
    RIGHT = None
    UP = None
    Down = None

    def __init__(self, pin, name):
        self.pin = pin
        self.name = name


Button.LEFT = Button(D0, "Left")
Button.RIGHT = Button(D3, "Right")
Button.UP = Button(D2, "Up")
Button.Down = Button(D1, "Down")

BUTTONS = [
    Button.LEFT,
    Button.RIGHT,
    Button.UP,
    Button.Down,
]

BUTTON_PINS = [button.pin for button in BUTTONS]


class RadioState:
    """Radio State Enumeration"""

    ADVERTISING = None
    CONNECTED = None
    OFF = None


RadioState.ADVERTISING = RadioState()
RadioState.CONNECTED = RadioState()
RadioState.OFF = RadioState()


class BatteryState:
    """Battery State Enumeration"""

    OK = None
    LOW = None
    CHARGING = None


BatteryState.OK = BatteryState()
BatteryState.LOW = BatteryState()
BatteryState.CHARGING = BatteryState()


class LEDState:
    """LED State Enumeration"""

    OFF = None
    SOLID = None
    BLINK = None


LEDState.OFF = LEDState()
LEDState.SOLID = LEDState()
LEDState.BLINK = LEDState()


class BatteryData:
    def __init__(self, state, level):
        self.__state = state
        self.__level = level

    def get_state(self):
        return self.__state

    def set_state(self, state):
        if state == self.__state:
            return

        self.__state = state

        str = ""

        if state is BatteryState.CHARGING:
            str = "Charging"
        elif state is BatteryState.LOW:
            str = "Low"
        elif state is BatteryState.OK:
            str = "Ok"
        else:
            raise ValueError("Unknown battery state")

        print(f"Battery state: {str}")

    def get_Level(self):
        return self.__level

    def set_level(self, level):
        self.__level *= 0.9
        self.__level += 0.1 * level

        print(f"Battery level: {self.__level}")


class SystemState:
    def __init__(self):
        self.__radio = RadioState.OFF
        self.__battery = BatteryData(BatteryState.OK, 3.7)
        self.__led = {
            LED_RED: LEDState.OFF,
            LED_GREEN: LEDState.OFF,
            LED_BLUE: LEDState.OFF,
        }
        self.__pressed = []
        self.__released = [Button.LEFT, Button.RIGHT, Button.UP, Button.Down]

    def get_pressed_buttons(self):
        return self.__pressed

    def press_button(self, button):
        if button in self.__released:
            self.__released.remove(button)

        print(f"{button.name} pressed")

        self.__pressed.append(button)

    def release_button(self, button):
        if button in self.__pressed:
            self.__pressed.remove(button)

        print(f"{button.name} released")

        self.__released.append(button)

    def get_radio_state(self):
        return self.__radio

    def set_radio_state(self, state):
        if state == self.__radio:
            return

        self.__radio = state

        str = ""

        if state is RadioState.ADVERTISING:
            str = "Advertising"
        elif state is RadioState.CONNECTED:
            str = "Connected"
        elif state is RadioState.OFF:
            str = "Off"
        else:
            raise ValueError("Unknown radio state")

        print(f"Radio state: {str}")

    def get_battery_data(self):
        return self.__battery

    def set_battery_data(self, state, level):
        self.__battery.set_level(level)
        self.__battery.set_state(state)

    def get_led_state(self, led):
        return self.__led[led]

    def set_led_state(self, led, state):
        if state == self.__led[led]:
            return

        self.__led[led] = state

        str = ""

        if state is LEDState.SOLID:
            str = "Solid"
        elif state is LEDState.BLINK:
            str = "Blink"
        elif state is LEDState.OFF:
            str = "Off"
        else:
            raise ValueError("Unknown LED state")

        print(f"LED: {led}, state: {str}")


async def ble_communicator(state):
    state.set_radio_state(RadioState.OFF)

    radio = BLERadio()

    battery = BatteryService()
    hid = HIDService()
    # device_info = DeviceInfoService(software_revision=1)

    advertisement = ProvideServicesAdvertisement(hid, battery)
    advertisement.appearance = 961

    scan_response = Advertisement()
    scan_response.complete_name = "BLE HID Ring"

    while True:
        radio.start_advertising(advertisement)

        state.set_radio_state(RadioState.ADVERTISING)

        while not radio.connected:
            await asyncio.sleep(0.25)

        radio.stop_advertising()

        state.set_radio_state(RadioState.CONNECTED)

        while radio.connected:
            await asyncio.sleep(0.25)


async def status_coordinator(state):
    while True:
        if state.get_radio_state() is RadioState.ADVERTISING:
            state.set_led_state(LED_BLUE, LEDState.BLINK)
        else:
            state.set_led_state(LED_BLUE, LEDState.OFF)

        batt = state.get_battery_data()

        if batt.get_state() is BatteryState.CHARGING:
            state.set_led_state(LED_RED, LEDState.OFF)
            state.set_led_state(LED_GREEN, LEDState.BLINK)
        elif batt.get_state() is BatteryState.LOW:
            state.set_led_state(LED_RED, LEDState.BLINK)
            state.set_led_state(LED_GREEN, LEDState.OFF)
        else:
            state.set_led_state(LED_RED, LEDState.OFF)
            state.set_led_state(LED_GREEN, LEDState.OFF)

        await asyncio.sleep(0.250)


async def button_monitor(state):
    buttons = Keys(BUTTON_PINS, value_when_pressed=False, pull=True)

    while True:
        event = buttons.events.get()

        if event:
            button_number = event.key_number
            # A key transition occurred.
            if event.pressed:
                state.press_button(BUTTONS[button_number])

            if event.released:
                state.release_button(BUTTONS[button_number])

        await asyncio.sleep(0)


async def battery_monitor(state):
    with Battery() as batt:
        while True:
            voltage = batt.voltage

            batt_state = BatteryState.OK

            if not batt.charge_status:
                batt_state = BatteryState.CHARGING

            elif voltage <= 3.6:
                batt_state = BatteryState.LOW

            state.set_battery_data(batt_state, voltage)

            await asyncio.sleep(20)


async def imu_monitor(state):
    while True:
        while state.get_radio_state() in [RadioState.ADVERTISING, RadioState.OFF]:
            await asyncio.sleep(1)

        print("Turning on IMU")

        with IMU() as imu:
            sensor = LSM6DS3(imu.i2c_bus)

            while state.get_radio_state() is RadioState.CONNECTED:
                print(
                    "Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2"
                    % (sensor.acceleration)
                )
                print("Gyro X:%.2f, Y: %.2f, Z: %.2f radians/s" % (sensor.gyro))

                await asyncio.sleep(0.2)

        print("Turning off IMU")


async def led_output(pin, state):
    with DigitalInOut(pin) as led:
        led.switch_to_output(value=False)

        while True:
            if state.get_led_state(pin) is LEDState.BLINK:
                led.value ^= True
            elif state.get_led_state(pin) is LEDState.SOLID:
                led.value = False
            elif state.get_led_state(pin) is LEDState.OFF:
                led.value = True

            await asyncio.sleep(0.5)


async def main():
    state = SystemState()

    ble_task = asyncio.create_task(ble_communicator(state))
    button_task = asyncio.create_task(button_monitor(state))
    battery_task = asyncio.create_task(battery_monitor(state))
    imu_task = asyncio.create_task(imu_monitor(state))
    status_task = asyncio.create_task(status_coordinator(state))
    red_led_task = asyncio.create_task(led_output(LED_RED, state))
    green_led_task = asyncio.create_task(led_output(LED_GREEN, state))
    blue_led_task = asyncio.create_task(led_output(LED_BLUE, state))

    await asyncio.gather(
        ble_task,
        status_task,
        button_task,
        battery_task,
        imu_task,
        red_led_task,
        green_led_task,
        blue_led_task,
    )

    print("done")


asyncio.run(main())
