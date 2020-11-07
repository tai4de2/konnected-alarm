# Copyright (c) 2020 Ted Miller. All rights reserved.

import ted_logger
import typing

from discovery import DiscoveredPanel
from pin_desc import PinCategory, PinFunction

_LOGGER = ted_logger.get_logger(__name__)

class PinMapping:
    __TRIGGER_OR_ANY_SENSOR = (
        PinFunction.TRIGGER_ACTUATOR,
        PinFunction.BINARY_SENSOR, PinFunction.DIGITAL_SENSOR, PinFunction.ONEWIRE_SENSOR)
    __BINARY_SENSOR_ONLY = (PinFunction.BINARY_SENSOR,)
    __ALARM_OR_TRIGGER = (PinFunction.ALARM_ACTUATOR, PinFunction.TRIGGER_ACTUATOR)
    __ALARM_ACTUATOR_ONLY = (PinFunction.ALARM_ACTUATOR,)
    __TRIGGER_ACTUATOR_ONLY = (PinFunction.TRIGGER_ACTUATOR,)

    # (pin/zone # or name, functions, user-selectable, category, label)
    _PRO_PIN_MAPPING = (
        (1, __TRIGGER_OR_ANY_SENSOR, True, PinCategory.ZONE, "Zone 1"),
        (2, __TRIGGER_OR_ANY_SENSOR, True, PinCategory.ZONE, "Zone 2"),
        (3, __TRIGGER_OR_ANY_SENSOR, True, PinCategory.ZONE, "Zone 3"),
        (4, __TRIGGER_OR_ANY_SENSOR, True, PinCategory.ZONE, "Zone 4"),
        (5, __TRIGGER_OR_ANY_SENSOR, True, PinCategory.ZONE, "Zone 5"),
        (6, __TRIGGER_OR_ANY_SENSOR, True, PinCategory.ZONE, "Zone 6"),
        (7, __TRIGGER_OR_ANY_SENSOR, True, PinCategory.ZONE, "Zone 7"),
        (8, __TRIGGER_OR_ANY_SENSOR, True, PinCategory.ZONE, "Zone 8"),
        (9, __BINARY_SENSOR_ONLY, False, PinCategory.ZONE, "Zone 9"),
        (10, __BINARY_SENSOR_ONLY, False, PinCategory.ZONE, "Zone 10"),
        (11, __BINARY_SENSOR_ONLY, False, PinCategory.ZONE, "Zone 11"),
        (12, __BINARY_SENSOR_ONLY, False, PinCategory.ZONE, "Zone 12"),
        ("alarm1", __ALARM_ACTUATOR_ONLY, False, PinCategory.OUTPUT_ONLY, "Alarm 1"),
        ("out1", __TRIGGER_ACTUATOR_ONLY, False, PinCategory.OUTPUT_ONLY, "Out 1"),
        ("alarm2_out2", __ALARM_OR_TRIGGER, False, PinCategory.OUTPUT_ONLY, "Alarm2/Out2"))

    __PHYSICAL_INDEX = 0
    __FUNCTION_INDEX = 1
    __SELECTABLE_INDEX = 2
    __CATEGORY_INDEX = 3
    __LABEL_INDEX = 4

    def __init__(self, discovered_panel: DiscoveredPanel):
        _LOGGER.debug("initializing pin mapping for model '%s'", discovered_panel.model_name)

        # Only for Konnected Pro for now.
        assert discovered_panel.model_name == "Konnected Pro"
        self._mapping = PinMapping._PRO_PIN_MAPPING
        self._use_zones = True

        pin_count = len(self._mapping)
        self._valid_functions = [None] * pin_count
        self._assigned_functions = [PinFunction.NONE] * pin_count

    def pin_count(self) -> int:
        """
        Gets the number of pins.
        """
        return len(self._mapping)

    def pin_functions(self, pin_ordinal: int) -> typing.Tuple:
        """
        Gets the functions a pin can perform. Note that these are not always user-selectable; some may be
        controlled by a physical switch on the panel.
        """
        return self._mapping[pin_ordinal][PinMapping.__FUNCTION_INDEX]

    def is_pin_function_user_selectable(self, pin_ordinal: int) -> bool:
        """
        Returns a value indicating whether a pin's function is user-selectable, or is hard-coded either by
        a physical switch on the panel. False is also returned if there's only a single possible function
        for the pin.
        """
        return self._mapping[pin_ordinal][PinMapping.__SELECTABLE_INDEX]

    def pin_category(self, pin_ordinal: int) -> PinCategory:
        """
        Gets a pin's category (zone, output-ßonly).
        """
        return self._mapping[pin_ordinal][PinMapping.__CATEGORY_INDEX]

    def pin_label(self, pin_ordinal: int) -> int:
        """
        Returns a pin's label.
        """
        return self._mapping[pin_ordinal][PinMapping.__LABEL_INDEX]

    def pin_panel_designator(self, pin_ordinal: int) -> typing.Tuple[str, typing.Any]:
        """
        Gets the label and value used in provisioning JSON for a pin.
        """
        return ("zone" if self._use_zones else "pin"), self._mapping[pin_ordinal][PinMapping.__PHYSICAL_INDEX]
