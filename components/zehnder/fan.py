import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import fan
from esphome.const import CONF_UPDATE_INTERVAL

from esphome.components.nrf905 import nRF905Component


DEPENDENCIES = ["nrf905"]

zehnder_ns = cg.esphome_ns.namespace("zehnder")
ZehnderRF = zehnder_ns.class_("ZehnderRF", cg.Component, fan.Fan)

CONF_NRF905 = "nrf905"
CONF_NETWORK_ID = "network_id"
CONF_DEVICE_ID = "my_device_id"
CONF_DEVICE_TYPE = "my_device_type"
CONF_MAIN_UNIT_ID = "main_unit_id"
CONF_MAIN_UNIT_TYPE = "main_unit_type"

# Device types, see the FAN_TYPE_* enum in zehnder.h
FAN_TYPE_MAIN_UNIT = 0x01
FAN_TYPE_REMOTE_CONTROL = 0x03

# Supplying any of these means discovery is skipped, so they only make sense together
_PAIRING_KEYS = (CONF_NETWORK_ID, CONF_MAIN_UNIT_ID, CONF_DEVICE_ID)


def _validate_pairing(config):
    present = [key for key in _PAIRING_KEYS if key in config]
    if present and len(present) != len(_PAIRING_KEYS):
        missing = ", ".join(key for key in _PAIRING_KEYS if key not in config)
        raise cv.Invalid(
            f"{missing} must be set as well when configuring the pairing manually. "
            f"Leave all of {', '.join(_PAIRING_KEYS)} out to pair over RF instead."
        )
    return config


CONFIG_SCHEMA = cv.All(
    fan.fan_schema(ZehnderRF)
    .extend(
        {
            cv.Required(CONF_NRF905): cv.use_id(nRF905Component),
            cv.Optional(CONF_UPDATE_INTERVAL, default="30s"): cv.update_interval,
            cv.Optional(CONF_NETWORK_ID): cv.hex_uint32_t,
            cv.Optional(CONF_MAIN_UNIT_ID): cv.hex_uint8_t,
            cv.Optional(
                CONF_MAIN_UNIT_TYPE, default=FAN_TYPE_MAIN_UNIT
            ): cv.hex_uint8_t,
            cv.Optional(CONF_DEVICE_ID): cv.hex_uint8_t,
            cv.Optional(
                CONF_DEVICE_TYPE, default=FAN_TYPE_REMOTE_CONTROL
            ): cv.hex_uint8_t,
        }
    )
    .extend(cv.COMPONENT_SCHEMA),
    _validate_pairing,
)


async def to_code(config):
    var = await fan.new_fan(config)
    await cg.register_component(var, config)

    nrf905 = await cg.get_variable(config[CONF_NRF905])
    cg.add(var.set_rf(nrf905))

    cg.add(var.set_update_interval(config[CONF_UPDATE_INTERVAL]))

    if CONF_NETWORK_ID in config:
        cg.add(
            var.set_static_pairing(
                config[CONF_NETWORK_ID],
                config[CONF_DEVICE_TYPE],
                config[CONF_DEVICE_ID],
                config[CONF_MAIN_UNIT_TYPE],
                config[CONF_MAIN_UNIT_ID],
            )
        )
