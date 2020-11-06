# Copyright (c) 2020 Ted Miller. All rights reserved.

import enum

class PinCategory(enum.Enum):
    ZONE = enum.auto()
    OUTPUT_ONLY = enum.auto()

class PinFunction(enum.Enum):
    NONE = enum.auto()
    BINARY_SENSOR = enum.auto()
    DIGITAL_SENSOR = enum.auto()
    ONEWIRE_SENSOR = enum.auto()
    ALARM_ACTUATOR = enum.auto()
    TRIGGER_ACTUATOR = enum.auto()
