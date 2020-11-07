# Copyright (c) 2020 Ted Miller. All rights reserved.

# Probably also need a separate class to monitor the zones, perform actuation, etc.
# Call these "monitor" + "actuator"... or maybe just "panel" that does all of those things.

# Functions:
# Initialize: loads yaml file with config (provisioning etc.); performs discovery
# Provision: performs provisioning; waits for panel to restart (we can know that from discovery...)
# Arm: arms, in either away or stay modes; starts listening for zone changes
# Disarm: takes a code and attempts to disarm
# Panic: set off siren
# Get-State
# Get-Zone-State(s)
# Get-Output-State(s)
#
# Events:
# Discovering
# Ready/Error (from Initialize)
# State Changed: ready, arming (delay), armed, triggered (within grace period), alarming, offline
# Zone Changed: ready, triggered
# Output Changed: unactuated, actuated

class Controller:
    pass