"""
Support for transport.opendata.ch.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.swiss_public_transport/
"""
import logging
from datetime import timedelta, datetime

import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, ATTR_ATTRIBUTION
import homeassistant.util.dt as dt_util
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
_RESOURCE = 'http://transport.opendata.ch/v1/'

ATTR_DEPARTURE_TIME1 = 'next_departure'
ATTR_DEPARTURE_TIME2 = 'next_on_departure'
ATTR_REMAINING_TIME = 'remaining_time'
ATTR_START = 'start'
ATTR_TARGET = 'destination'

CONF_ATTRIBUTION = "Data provided by metlink.org.nz"

DEFAULT_NAME = 'Next Departure'
ICON = 'mdi:bus'

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)
TIME_STR_FORMAT = "%H:%M"

# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
#     vol.Required('stop_numbers'): cv.arry,
#     vol.Required(CONF_START): cv.string,
#     vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
# })


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Get the Metlink public transport sensor."""
    # journal contains [0] Station ID start, [1] Station ID destination
    # [2] Station name start, and [3] Station name destination
    stop_number = config.get('stop_number')
    add_devices([MetlinkSensor(stop_number)])


class MetlinkSensor(Entity):
    """Implementation of an Metlink public transport sensor."""

    def __init__(self, stop_number):
        """Initialize the sensor."""
        self.stop_number = stop_number
        self._name = 'stop_{stop_number}'.format(stop_number=stop_number)
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._data.get('Services')[0].get('DepartureStatus')

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        """
        {'IsRealtime': True, 'Direction': 'Inbound', 'ExpectedDeparture': '2017-04-13T22:33:39+12:00',
        'Service': {'Code': '11', 'TrimmedCode': '11', 'Link': '/timetables/bus/11', 'Mode': 'Bus',
        'Name': 'Seatoun - Wellington'}, 'AimedDeparture': '2017-04-13T22:31:00+12:00',
        'DestinationStopID': '5016', 'OriginStopName': 'SeatounPk-HectorSt',
        'OriginStopID': '7042', 'ServiceID': '11',
        'AimedArrival': '2017-04-13T22:31:00+12:00',
        'VehicleFeature': 'lowFloor', 'VehicleRef': '1427',
        'DepartureStatus': 'delayed', 'OperatorRef': 'NZBS',
        'DisplayDepartureSeconds': 321,
        'DestinationStopName': 'Wgtn Station', 'DisplayDeparture': '2017-04-13T22:33:39+12:00'}

        """
        attributes = {'name': self._stop_info.get('Name')}
        for service in self._data.get('Services'):
            _LOGGER.info(service)
            service_label = "{service_id} {service_name}".format(
                service_id=service.get('Service').get('Code'),
                service_name=service.get('Service').get('Name')
            )
            service_time = datetime.strptime(service.get(
                'AimedDeparture'), "%Y-%m-%dT%H:%M:%S+12:00")
            attributes[service_time.strftime('%H:%M %a')] = service_label
        return attributes

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    def update(self):
        """Get the latest data from opendata.ch and update the states."""
        url = "https://www.metlink.org.nz/api/v1/StopDepartures/{stop_number}".format(
            stop_number=self.stop_number)
        r = requests.get(url)
        self._data = r.json()
        self._stop_info = self._data.get('Stop')
