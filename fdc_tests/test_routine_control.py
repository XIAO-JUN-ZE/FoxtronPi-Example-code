from uds.connection import DoIPConnection
from uds.client_config import client_config
import udsoncan
import datetime
import time
import struct
from udsoncan.client import Client
from udsoncan.services import *
from typing import Optional
from udsoncan import services
from enum import Enum


class PowerConstraint(Enum):
    EMPTY = 0x00
    ON = 0x01
    OFF = 0x02
    STANDBY = 0x03


class PowerState(Enum):
    OFF = 0x00
    OFFC = 0x01
    OFFA = 0x02
    STANDBY = 0x03
    ON = 0x04
    READY = 0x05


def debug_print(msg):
    print(f"{datetime.datetime.now()}: {msg}")


def test_routine_control_dfff_power_on_vehicle(doip_client):

    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        ## Arrange
        response = client.change_session(0x03)
        assert response.positive
        assert response.service_data.session_echo == 3

        response = client.unlock_security_access(3)
        assert response.positive

        response = request_pwr_constriant(client, PowerConstraint.OFF, PowerState.OFFA)
        assert response.positive

        ## Act
        response = request_pwr_constriant(client, PowerConstraint.ON, PowerState.ON)

        ## Assert
        assert response.positive
        assert response.service_data.routine_status_record[0] == 0x04


def test_routine_control_dfff_power_off_vehicle(doip_client):

    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=(client_config())) as client:
        # Arange
        response = client.change_session(0x03)
        assert response.positive
        assert response.service_data.session_echo == 3
        response = client.unlock_security_access(3)
        assert response.positive

        response = request_pwr_constriant(client, PowerConstraint.ON, PowerState.ON)
        assert response.positive

        # Act
        response = request_pwr_constriant(client, PowerConstraint.OFF, PowerState.OFFA)
        response = request_pwr_constriant(client, PowerConstraint.OFF, PowerState.OFF)

        # Assert
        assert response.positive
        assert response.service_data.routine_status_record[0] == 0x00


def test_routine_control_dfff_power_standby_vehicle(doip_client):

    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        # Arange
        response = client.change_session(0x03)
        assert response.positive
        assert response.service_data.session_echo == 3
        response = client.unlock_security_access(3)
        assert response.positive
        response = request_pwr_constriant(client, PowerConstraint.ON, PowerState.ON)
        assert response.positive

        # Act
        response = request_pwr_constriant(
            client, PowerConstraint.STANDBY, PowerState.OFFA
        )
        response = request_pwr_constriant(
            client, PowerConstraint.STANDBY, PowerState.STANDBY
        )

        # Assert
        assert response.positive
        assert response.service_data.routine_status_record[0] == 0x03


def request_pwr_constriant(
    client: Client, constraint: PowerConstraint, expect: PowerState
) -> Optional[services.RoutineControl.InterpretedResponse]:

    start = time.time()
    # This timeout is refers to the PMM spec.
    timeout = 12

    response = client.routine_control(
        0xDFFF, control_type=0x01, data=bytes([constraint.value])
    )
    assert response.positive

    while time.time() - start < timeout:
        response = client.get_routine_result(0xDFFF)

        if (
            response.positive
            and response.service_data.routine_status_record[0] == expect.value
        ):
            break
        time.sleep(1)
    else:
        assert False

    return response


def test_when_routine_control_0204_then_imu_calibration_success(doip_client):

    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        # Arange
        response = client.change_session(
            DiagnosticSessionControl.Session.extendedDiagnosticSession
        )
        debug_print(response)
        assert response.positive

        response = client.unlock_security_access(1)
        debug_print(response)
        assert response.positive

        boundary_acceleration = 0x0102
        boundary_gyro = 0x0304
        permissible_error_counter = 0x0506
        option_record = struct.pack(
            ">HHH", boundary_acceleration, boundary_gyro, permissible_error_counter
        )
        debug_print(f"option_record: {option_record}")

        # Act
        response = client.start_routine(0x0204, option_record)
        debug_print(response)

        # Assert
        assert response.positive
