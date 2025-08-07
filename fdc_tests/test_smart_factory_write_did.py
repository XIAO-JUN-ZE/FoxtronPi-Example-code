from uds.connection import DoIPConnection
from uds.client_config import client_config
import udsoncan
import datetime
from udsoncan.client import Client
from udsoncan.services import *
import json


def debug_print(msg):
    print(f"{datetime.datetime.now()}: {msg}")


def test_given_correct_data_when_write_did_07f1_then_positive_response(doip_client):
    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.change_session(
            DiagnosticSessionControl.Session.extendedDiagnosticSession
        )
        assert response.positive
        assert response.service_data.session_echo == 3

        response = client.unlock_security_access(0x03)
        assert response.positive

        data_dict = [
            {
                "production_station": "EOL_ESC",
                "test_results": [
                    {
                        "test_item": "DID7777",
                        "test_judgement": "XX",
                        "test_log": "test log long text long text long text",
                        "test_value": "XX",
                    }
                ],
                "uid": "user999",
                "vin_code": "D31LMHPCL11A003190",
            },
            {
                "production_station": "EOL_ESC",
                "test_results": [
                    {
                        "test_item": "DID0000",
                        "test_judgement": "XX",
                        "test_log": "test log long text long text long text",
                        "test_value": "XX",
                    }
                ],
                "uid": "user777",
                "upload_time": "2024-11-14 10:04:05",
                "vin_code": "D31LMHPCL11A003190",
            },
        ]

        json_data = json.dumps(data_dict)
        data = json_data.encode("ascii")

        print(len(data))

        # Act
        response = client.write_data_by_identifier(0x07F1, data)

        # Assert
        assert response.positive
        assert response.service_data.did_echo == 0x07F1
