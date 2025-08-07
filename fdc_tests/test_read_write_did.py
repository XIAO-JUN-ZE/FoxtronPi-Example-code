from uds.connection import DoIPConnection
from uds.client_config import client_config
import udsoncan
import datetime
from udsoncan.client import Client
from udsoncan.services import *


def debug_print(msg):
    print(f"{datetime.datetime.now()}: {msg}")


def test_read_write_vin_f190(doip_client):

    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        read_vin = client.read_data_by_identifier(0xF190)
        assert read_vin.positive

        debug_print(read_vin.service_data.values[0xF190])

        response = client.change_session(
            DiagnosticSessionControl.Session.extendedDiagnosticSession
        )
        assert response.positive
        assert response.service_data.session_echo == 3
        response = client.unlock_security_access(1)
        assert response.positive

        response = client.write_data_by_identifier(
            0xF190, bytes("RF5D31LHT00ET7047", "ascii")
        )
        assert response.positive
        assert response.service_data.did_echo == 0xF190

        response = client.read_data_by_identifier(0xF190)
        assert response.positive
        assert response.service_data.values[0xF190] == (b"RF5D31LHT00ET7047",)

        debug_print(response.service_data.values[0xF190])

        response = client.write_data_by_identifier(
            0xF190, read_vin.service_data.values[0xF190]
        )
        assert response.positive

        response = client.read_data_by_identifier(0xF190)
        assert response.positive
        assert (
            response.service_data.values[0xF190] == read_vin.service_data.values[0xF190]
        )

        debug_print(response.service_data.values[0xF190])


def test_read_write_fvt_vin_f090(doip_client):

    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        read_fvt_vin = client.read_data_by_identifier(0xF090)
        assert read_fvt_vin.positive

        debug_print(read_fvt_vin.service_data.values[0xF090])

        response = client.change_session(
            DiagnosticSessionControl.Session.extendedDiagnosticSession
        )
        assert response.positive
        assert response.service_data.session_echo == 3
        response = client.unlock_security_access(1)
        assert response.positive

        response = client.write_data_by_identifier(
            0xF090, bytes("D31MMPC123456L11B-----", "ascii")
        )
        assert response.positive
        assert response.service_data.did_echo == 0xF090

        response = client.read_data_by_identifier(0xF090)
        assert response.positive
        assert response.service_data.values[0xF090] == (b"D31MMPC123456L11B-----",)

        debug_print(response.service_data.values[0xF090])

        response = client.write_data_by_identifier(
            0xF090, read_fvt_vin.service_data.values[0xF090]
        )
        assert response.positive

        response = client.read_data_by_identifier(0xF090)
        assert response.positive
        assert (
            response.service_data.values[0xF090]
            == read_fvt_vin.service_data.values[0xF090]
        )

        debug_print(response.service_data.values[0xF090])


def test_read_write_xwd_0201(doip_client):

    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        read_xwd = client.read_data_by_identifier(0x0201)
        assert read_xwd.positive

        debug_print(read_xwd.service_data.values[0x0201])

        response = client.change_session(
            DiagnosticSessionControl.Session.extendedDiagnosticSession
        )
        assert response.positive
        assert response.service_data.session_echo == 3
        response = client.unlock_security_access(1)
        assert response.positive

        response = client.write_data_by_identifier(0x0201, bytes(0x01))
        assert response.positive
        assert response.service_data.did_echo == 0x0201

        response = client.read_data_by_identifier(0x0201)
        assert response.positive
        assert response.service_data.values[0x0201] == (bytes(0x01),)

        debug_print(response.service_data.values[0x0201])

        response = client.write_data_by_identifier(
            0x0201, read_xwd.service_data.values[0x0201]
        )
        assert response.positive

        response = client.read_data_by_identifier(0x0201)
        assert response.positive
        assert (
            response.service_data.values[0x0201] == read_xwd.service_data.values[0x0201]
        )

        debug_print(response.service_data.values[0x0201])


# TODO: Implement this test, since the DKC length is 8 bytes,
# the test should be able to read and write the DKC.
# def test_read_write_dkc_0202(doip_client):

#     assert doip_client.is_open()
#     udsoncan.setup_logging()
#     connection = DoIPConnection(doip_client)

#     assert connection.is_open()
#     with Client(connection, config=client_config()) as client:
#         read_dkc= client.read_data_by_identifier(0x0202)
#         assert read_dkc.positive

#         debug_print(read_dkc.service_data.values[0x0202])

#         response = client.change_session(
#             DiagnosticSessionControl.Session.extendedDiagnosticSession
#         )
#         assert response.positive
#         assert response.service_data.session_echo == 3
#         response = client.unlock_security_access(5)
#         assert response.positive

#         response = client.write_data_by_identifier(0x0202, bytes(0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07))
#         assert response.positive
#         assert response.service_data.did_echo == 0x0202


#         response = client.read_data_by_identifier(0x0202)
#         assert response.positive

#         debug_print(response.service_data.values[0x0202])

#         response = client.write_data_by_identifier(0x0202, read_dkc.service_data.values[0x0202])
#         assert response.positive

#         response = client.read_data_by_identifier(0x0202)
#         assert response.positive

#         debug_print(response.service_data.values[0x0202])
