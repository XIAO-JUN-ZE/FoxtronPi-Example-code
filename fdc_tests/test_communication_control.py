from uds.connection import DoIPConnection
from uds.client_config import client_config
import udsoncan
import datetime
from udsoncan.client import Client
from udsoncan.services import *


def test_communication_control_disable_normalCommunicationMessages(doip_client):
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.change_session(0x03)
        assert response.positive
        assert response.service_data.session_echo == 3
        response = client.unlock_security_access(1)
        assert response.positive
        # 0x03 is disable normal communication messages
        response = client.communication_control(
            control_type=0x03, communication_type=0x01
        )
        assert response.positive


def test_communication_control_enable_normalCommunicationMessages(doip_client):
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.change_session(0x03)
        assert response.positive
        assert response.service_data.session_echo == 3
        response = client.unlock_security_access(1)
        assert response.positive
        # 0x00 is enable normal communication messages
        response = client.communication_control(
            control_type=0x00, communication_type=0x01
        )
        assert response.positive
