import asyncio

from adafruit_lsm6ds.lsm6ds3 import LSM6DS3
from enum import Enum
from data_producer import DataProducer
from vector import Vecotr
from seeed_xiao_nrf52840 import IMU


class IMUState(Enum):
    STOPPING = None
    STOPPED = None
    COLLECTING_CENTER = None
    CENTERED = None
    ROLLED_CW = None
    ROLLED_HARD_CW = None
    ROLLED_CCW = None
    ROLLED_HARD_CCW = None


IMUState.STOPPING = IMUState()
IMUState.STOPPED = IMUState()
IMUState.COLLECTING_CENTER = IMUState()
IMUState.CENTERED = IMUState()
IMUState.ROLLED_CW = IMUState()
IMUState.ROLLED_HARD_CW = IMUState()
IMUState.ROLLED_CCW = IMUState()
IMUState.ROLLED_HARD_CCW = IMUState()


class IMUMonitor(DataProducer):
    """watches the IMU"""

    OFFSET_SAMPLES = 10
    SAMPLE_PERIOD_S = 0.01

    def __init__(self):
        super().__init__()

        self.__state = IMUState.STOPPED
        self.__event = asyncio.Event()

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        if value is self.__state:
            return

        self.__state = value

        print(f"IMU State: {self.state}")

        self.notify_callback()

    def start(self):
        if self.state not in [RadioState.STOPPED, RadioState.STOPPING]:
            return FALSE

        self.state = RadioState.COLLECTING_CENTER
        self.__event.set()

        return TRUE

    def stop(self):
        if self.state in [RadioState.STOPPED, RadioState.STOPPING]:
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

    @property
    async def task(self):
        while True:
            await self.__event_wait()

            print("Turning on IMU")

            zero_offset = None
            last_vector = None
            offset_samples = []

            with IMU() as imu:
                sensor = LSM6DS3(imu.i2c_bus)

                while self.state is not IMUState.STOPPED:
                    sample = sensor.acceleration
                    vector = Vector(sample[0], sample[1], sample[2]).normalized

                    if self.state is IMUState.COLLECTING_OFFSET:
                        offset_samples.append(vector)

                        if len(offset_samples) >= self.OFFSET_SAMPLES:
                            zero_offset = calculate_zero_offset(offset_samples)
                            last_vector = zero_offset

                            self.state = IMUState.CENTERED

                    else:
                        last_vector = update_sample(last_vector, vector)

                        angle = zero_offset.angle_to(vector)

                        if angle > self.HARD_ROLL_ANGLE:
                            self.state = IMUState.ROLLED_HARD_CW
                        if (angle <= self.HARD_ROLL_ANGLE) and (
                            angle > self.ROLL_ANGLE
                        ):
                            self.state = IMUState.ROLLED_CW
                        if (angle <= self.ROLL_ANGLE) and (angle >= -self.ROLL_ANGLE):
                            self.state = IMUState.CENTERED
                        if (angle >= -self.HARD_ROLL_ANGLE) and (
                            angle < -self.ROLL_ANGLE
                        ):
                            self.state = IMUState.ROLLED_CCW
                        if angle < self.HARD_ROLL_ANGLE:
                            self.state = IMUState.ROLLED_HARD_CCW

                    await self.__event_wait(self.SAMPLE_PERIOD_S)

            print("Turning off IMU")

    def calculate_zero_offset(vectors):
        x_avg = [v.x for v in vectors] / len(vectors)
        y_avg = [v.y for v in vectors] / len(vectors)
        z_avg = [v.z for v in vectors] / len(vectors)

        return Vector(x_avg, y_avg, z_avg)

    def update_sample(v1, v2):
        x = (v1.x * 0.9) + (v2.x * 0.1)
        y = (v1.y * 0.9) + (v2.y * 0.1)
        z = (v1.z * 0.9) + (v2.z * 0.1)

        return Vector(x, y, z)
