"""
GPIO pulse counter and frequency sensors
"""

import datetime
from ...exceptions import RuntimeConfigError
from ...types import CerberusSchemaType, ConfigType, PinType, SensorValueType
from . import GenericSensor

CONFIG_SCHEMA: CerberusSchemaType = {
    "pin": dict(type="integer", required=True, empty=False),
}

pulse_counter = {}

def increment_pulse_count(pin: PinType) -> None:
    pulse_counter[pin]['counter'] += 1

class Sensor(GenericSensor):
    """
    Implementation of Sensor class for the GPIO pulse counter sensor.
    """

    SENSOR_SCHEMA: CerberusSchemaType = {
        "type": dict(
            type="string",
            required=False,
            empty=False,
            default="count",
            allowed=["count", "frequency"],
        )
    }

    def setup_module(self) -> None:
        self.pin: PinType = self.config["pin"]
        pulse_counter[self.pin] = {}
        pulse_counter[self.pin]['counter'] = 0
        pulse_counter[self.pin]['last_count'] = 0
        pulse_counter[self.pin]['last_time'] = None

    def get_value(self, sens_conf: ConfigType) -> SensorValueType:
        """
        Get the count or frequency value from the sensor
        """
        count: SensorValueType = pulse_counter[self.pin]['counter']
        time = datetime.datetime.now()

        if sens_conf["type"] == "count":
            return count
        if sens_conf["type"] == "frequency":
            freq: SensorValueType = 0.0
            if pulse_counter[self.pin]['last_time'] is not None:
                delta = count - pulse_counter[self.pin]['last_count']
                seconds = (time - pulse_counter[self.pin]['last_time']).total_seconds()
                freq = delta / seconds
            pulse_counter[self.pin]['last_time'] = time
            pulse_counter[self.pin]['last_count'] = count
            return freq
        raise RuntimeConfigError(
            "gpiopc sensor '%s' was not configured to return 'count' or 'frequency'"
            % sens_conf["name"]
        )
