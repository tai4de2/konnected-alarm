# Copyright (c) 2020 Ted Miller. All rights reserved.

import ted_logger
import urllib.request
import xml.dom
import xml.dom.minidom

from ssdpy import SSDPClient

_LOGGER = ted_logger.get_logger(__name__)

class DiscoveredPanel:
    """
    Information about a discovered endpoint.
    Fields:
    friendly_name, manufacturer, model_description, model_name, model_number, serial_number, st, url_base
    """
    pass

class Discoverer:
    """
    Discovers Konnected Alarm panels.
    """

    # Example SSDP search response:
    #
    # {'cache-control': 'max-age=1800',
    #  'st': 'urn:schemas-konnected-io:device:Security:2',
    #  'usn': 'uuid:8f655392-a778-4fee-97b9-964c11aef68d::urn:schemas-konnected-io:device:Security:2',
    #  'ext': '',
    #  'server': 'NodeMCU/0.1.0 UPnP/1.1 Konnected Pro/1.1.1',
    #  'location': 'http://192.168.0.165:9123/Device.xml' }


    # Example XML doc fetched from the "location" item in the SSDP notification response:
    #
    # <?xml version="1.0" ?>
    # <root configId="9123" xmlns="urn:schemas-upnp-org:device-1-0">
    #     <specVersion><major>1</major><minor>0</minor></specVersion>
    #     <URLBase>http://192.168.0.165:9123</URLBase>
    #     <device>
    #         <deviceType>urn:schemas-konnected-io:device:Security:2</deviceType>
    #         <friendlyName>Konnected Pro</friendlyName>
    #         <manufacturer>konnected.io</manufacturer>
    #         <manufacturerURL>http://konnected.io/</manufacturerURL>
    #         <modelDescription>Konnected Security</modelDescription>
    #         <modelName>Konnected Pro</modelName>
    #         <modelNumber>1.1.1</modelNumber>
    #         <serialNumber>0x964c11aef68d</serialNumber>
    #         <UDN>uuid:8f655392-a778-4fee-97b9-964c11aef68d</UDN>
    #         <presentationURL>/</presentationURL>
    #     </device>
    # </root>

    _DEVICE_ELEMENT_MAP = {
        "friendlyName": "friendly_name",
        "manufacturer": "manufacturer",
        "modelDescription": "model_description",
        "modelName": "model_name",
        "modelNumber": "model_number",
        "serialNumber": "serial_number"
    }

    _ROOT_ELEMENT_MAP = {
        "URLBase": "url_base",
        "device": _DEVICE_ELEMENT_MAP
    }

    _DISCOVERY_ST = "urn:schemas-konnected-io:device:Security"

    # Returns panel endpoint, or None.
    async def discover(self) -> DiscoveredPanel:
        _LOGGER.info("initiating SSDP discovery for '%s'", Discoverer._DISCOVERY_ST)

        ssdpClient = SSDPClient()

        # Bug in konnected alarm panel pro -- requires a space between the ST: header and the value.
        devices = ssdpClient.m_search(' ' + Discoverer._DISCOVERY_ST)

        if len(devices) == 0:
            _LOGGER.warning("no endpoints responsed to discovery search for '%s'", Discoverer._DISCOVERY_ST)
            return None

        # Just one for now.
        device = devices[0]
        st = device.get("st")
        location = device.get("location")
        if (st is None) or (len(st) == 0):
            _LOGGER.error(
                "st field in discovery response (search '%s') is missing or blank",
                Discoverer._DISCOVERY_ST)
            return None
        if (location is None) or (len(location) == 0):
            _LOGGER.error("location field for '%s' is missing or blank", st)
            return None

        deviceInfoXmlString = urllib.request.urlopen(location).read()
        deviceXml = xml.dom.minidom.parseString(deviceInfoXmlString)

        endpoint = DiscoveredPanel()
        Discoverer._initialize_empty_endpoint(Discoverer._ROOT_ELEMENT_MAP, endpoint)
        Discoverer._process_endpoint_xml(Discoverer._ROOT_ELEMENT_MAP, deviceXml.documentElement, endpoint)
        setattr(endpoint, "st", st)

        # Can't live without the URL.
        if len(endpoint.url_base) == 0:
            _LOGGER.error("url_base field for xml for '%s' is missing or blank", st)
            return None

        _LOGGER.info("found %s", repr(endpoint.__dict__))
        return endpoint

    @staticmethod
    def _initialize_empty_endpoint(map, endpoint):
        """
        Initializes all fields in a DiscoveredPanel to an empty string.
        """
        for v in map.values():
            if isinstance(v, str):
                setattr(endpoint, v, "")
            elif isinstance(v, dict):
                Discoverer._initialize_empty_endpoint(v, endpoint)

    @staticmethod
    def _process_endpoint_xml(map, element, endpoint):
        for node in element.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                tag = node.localName
                map_value = map.get(tag)

                if isinstance(map_value, str):
                    textNode = node.firstChild
                    if textNode.nodeType == xml.dom.Node.TEXT_NODE:
                        text = textNode.data
                        if len(text) > 0:

                            # First one wins
                            if len(getattr(endpoint, map_value)) == 0:
                                setattr(endpoint, map_value, text)

                elif isinstance(map_value, dict):
                    Discoverer._process_endpoint_xml(map_value, node, endpoint)
                    
                else:
                    assert map_value is None

