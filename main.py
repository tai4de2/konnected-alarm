#!python3
# Copyright (c) 2020 Ted Miller. All rights reserved.

import asyncio
import json
import discovery
import pin_desc
import pin_mapping
import provisioning
import requests
import ted_logger


_LOGGER = ted_logger.get_logger("main")

async def main():
    d = discovery.Discoverer()
    discovered_panel = await d.discover()
    if discovered_panel is None:
        print("No panels discovered")
    else:
        print(f"Discovered panel {discovered_panel.friendly_name} at {discovered_panel.url_base}")
        mapping = pin_mapping.PinMapping(discovered_panel)
        provisioner = provisioning.Provisioner(mapping)
        provisioner.provision(0, pin_desc.PinFunction.BINARY_SENSOR)
        provisioner.provision(1, pin_desc.PinFunction.BINARY_SENSOR)

        body = provisioner.create_payload(endpoint = "http://192.168.0.192:5556/path1/path2", token = "abc")
        response = requests.put(
            discovered_panel.url_base + "/settings",
            json = body)
        print(response.status_code)

_LOGGER.info("started")
asyncio.run(main())
