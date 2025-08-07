from uds.connection import DoIPConnection
from uds.client_config import client_config
import udsoncan
import datetime
from udsoncan.client import Client
from udsoncan.services import *


def debug_print(msg):
    print(f"{datetime.datetime.now()}: {msg}")


def test_read_did_sw_version_f195(doip_client):

    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.read_data_by_identifier(0xF195)
        assert response.positive
        debug_print(response.service_data.values[0xF195])


def test_read_did_hw_version_f193(doip_client):

    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.read_data_by_identifier(0xF193)
        assert response.positive
        debug_print(response.service_data.values[0xF193])


def test_read_did_hw_version_f16f(doip_client):

    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.read_data_by_identifier(0xF16F)
        assert response.positive
        debug_print(response.service_data.values[0xF16F])

def test_given_open_doip_client_when_read_did_partition_f181_then_success(doip_client):

    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()

    # Act
    with Client(connection, config=client_config()) as client:
        response = client.read_data_by_identifier(0xF181)

    # Assert
    assert response.positive
    debug_print(response.service_data.values[0xF181])
