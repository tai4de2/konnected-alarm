# Copyright (c) 2020 Ted Miller. All rights reserved.

import ted_logger
import typing

from discovery import DiscoveredPanel
from pin_mapping import PinMapping, PinFunction

_LOGGER = ted_logger.get_logger(__name__)

class Provisioner:

    def __init__(self, pin_mapping: PinMapping):
        self._pin_mapping = pin_mapping
        self._pin_provisioning = [PinFunction.NONE * pin_mapping.pin_count()]
        self._pin_extra = [None * pin_mapping.pin_count()]

    def provision_pin(
        self,
        pin_ordinal: int,
        function: PinFunction,
        *,
        sensor_poll_interval_minutes = None,
        actuator_trigger_high = None) -> None:
        """
        Provisions (or deprovisions) a pin.

        For deprovisioning, set pin function to NONE.
        For provisioning to a sensor pin function, supply a sensor poll interval.
        For provisioning to a actuator pin function, supply a trigger high/low value.
        """

        if (function == PinFunction.NONE) \
            or (function == PinFunction.BINARY_SENSOR) \
            or (function == PinFunction.ONEWIRE_SENSOR):
            if (sensor_poll_interval_minutes is not None) or (actuator_trigger_high is not None):
                raise ValueError(
                    f"For {function.name} pins, sensor poll interval and trigger high value "
                    + "must not be supplied")
            extra = None            

        elif function == PinFunction.DIGITAL_SENSOR:
            if (not isinstance(sensor_poll_interval_minutes, int)) or (actuator_trigger_high is not None):
                raise ValueError(f"For {function.name} pins, an integer sensor poll interval "
                    + "must be supplied, and a trigger high value must not be supplied")
            extra = sensor_poll_interval_minutes

        elif (function == PinFunction.ALARM_ACTUATOR) or (function == PinFunction.TRIGGER_ACTUATOR):
            if (sensor_poll_interval_minutes is not None) or (not isinstance(actuator_trigger_high, bool)):
                raise ValueError(f"For {function.name} pins, a sensor poll interval "
                    + "must not be supplied, and a trigger high bool value must be supplied")
            extra = actuator_trigger_high

        else:
            assert False

        if function not in self._pin_mapping.pin_functions(pin_ordinal):
            raise ValueError(f"Function {function.name} is not valid for pin {pin_ordinal}")

        self._pin_provisioning[pin_ordinal] = function
        self._pin_extra[pin_ordinal] = extra

        _LOGGER.info("pin %d provisioned as %s; extra=%s", pin_ordinal, function.name, extra)

    def get_pin_provisioning(self, pin_ordinal: int) -> PinFunction:
        """
        Gets provisioning state for a pin.
        """
        return self._pin_provisioning[pin_ordinal]

    def get_pin_provisioning_param(self, pin_ordinal: int) -> typing.Any:
        """
        Gets the parameter associated with a pin's provisioning.
        """
        return self._pin_extra[pin_ordinal]

    def create_payload(self, * endpoint: str, token: str) -> dict:
        """
        Creates a payload which can be sent to the panel to provision it. This does not actually send
        anything to the panel.
        """

        sensors = []
        digital_sensors = []
        actuators = []

        # Build up arrays related to pins.
        for i in range(len(self._pin_provisioning)):
            physical_number = self._pin_mapping.pin_physical_number(i)
            provisioned_as = self._pin_provisioning[i]
            extra = self._pin_extra[i]

            if (provisioned_as == PinFunction.BINARY_SENSOR) \
                or (provisioned_as == PinFunction.ONEWIRE_SENSOR):
                sensors.append({"pin": physical_number})

            elif provisioned_as == PinFunction.DIGITAL_SENSOR:
                digital_sensors.append({"pin": physical_number, "poll_interval": extra})

            elif (provisioned_as == PinFunction.ALARM_ACTUATOR) \
                or (provisioned_as == PinFunction.TRIGGER_ACTUATOR):
                actuators.append({"pin": physical_number, "trigger": 1 if extra else 0})

            else:
                assert provisioned_as == PinFunction.NONE

        # Build payload for rest API.
        rest = { "endpoint_type": "rest", "endpoint": endpoint, "token": token }
        if len(sensors) > 0:
            rest["sensors"] = sensors
        if len(digital_sensors) > 0:
            rest["dht_sensors"] = digital_sensors
        if len(actuators) > 0:
            rest["actuators"] = actuators

        return rest
