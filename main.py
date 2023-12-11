import asyncio

from battery import BatteryMonitor
from button import ButtonMonitor
from imu import IMUMonitor
from led import LEDCommunicator
from radio import Radio, RadioState
from system import SystemController

async def main():
    battery = BatteryMonitor()
    button = ButtonMonitor()
    imu = IMUMonitor()
    led = LEDCommunicator()
    radio = Radio()

    state = SystemController(battery, button, imu, led, radio)

    await asyncio.gather(
        *[
            battery.task,
            button.task,
            imu.task,
            led.task
            radio.task,
            state.task,
        ]
    )

asyncio.run(main())
