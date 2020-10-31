#!python3
# Copyright (c) 2020 Ted Miller. All rights reserved.

import asyncio
import discovery
import ted_logger

_LOGGER = ted_logger.get_logger("main")

async def main():
    d = discovery.Discoverer()
    x = await d.discover()

_LOGGER.info("started")
asyncio.run(main())
