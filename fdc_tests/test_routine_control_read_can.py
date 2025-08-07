from uds.connection import DoIPConnection
from uds.client_config import client_config
import udsoncan
import datetime
from udsoncan.client import Client
from udsoncan.services import *
import json
import time
import re
import dataclasses
import os
import pytest

OVERNIGHT_TEST = False
OVERNIGHT_TEST_FILE = "raw_can_data_20_ids_with_60s_over_night_"
HAPPY_PATH_TEST_FILE = "raw_can_data_20_ids_with_60s_happy_path"
KEEP_NEWEST_TEST_FILE = "raw_can_data_20_ids_with_60s_after_70s"
RESUBSCRIBE_TEST_FILE = "raw_can_data_20_ids_with_60s_resubscribe"


@dataclasses.dataclass
class RawCanData:
    timestamp: str
    channel: int
    can_id: int
    dlc: int
    data: str


# fmt: off
# Define data bytes for routine control
data = bytes([0x14,0x3C,
              0x01,0x00,0x00,0x05,0x00,
              0x01,0x00,0x00,0x03,0xC0,
              0x01,0x00,0x00,0x02,0x38,
              0x01,0x00,0x00,0x02,0x36,
              0x01,0x00,0x00,0x02,0x10,
              0x02,0x00,0x00,0x05,0x00,
              0x02,0x00,0x00,0x04,0x38,
              0x02,0x00,0x00,0x04,0x36,
              0x02,0x00,0x00,0x04,0x35,
              0x02,0x00,0x00,0x03,0xC3,
              0x03,0x00,0x00,0x01,0xF0,
              0x03,0x00,0x00,0x01,0x86,
              0x03,0x00,0x00,0x01,0x82,
              0x03,0x00,0x00,0x01,0x54,
              0x03,0x00,0x00,0x01,0x16,
              0x05,0x00,0x00,0x04,0xF3,
              0x05,0x00,0x00,0x01,0xC5,
              0x05,0x00,0x00,0x01,0x7A,
              0x05,0x00,0x00,0x01,0x18,
              0x05,0x00,0x00,0x07,0x77,
              ])
# fmt: on


def decode_raw_can_data(data, file_name="raw_can_data.json"):
    pattern = r"\{.*?\}"
    matchs = re.findall(pattern, data)
    json_objects = []
    for match in matchs:
        try:
            json_obj = json.loads(match)
            json_objects.append(json_obj)
        except json.JSONDecodeError as e:
            print(e)
    # Write to file and print total number of CAN messages
    with open(file_name, "w") as f:
        json.dump(json_objects, f)


def debug_print(msg):
    print(f"{datetime.datetime.now()}: {msg}")


def test_when_routine_control_0xdffe_then_correct_result(doip_client):
    # Test routine control with 20 CAN IDs 60 seconds

    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.change_session(0x03)
        assert response.positive
        response = client.unlock_security_access(0x03)
        assert response.positive

        # Act
        response = client.routine_control(0xDFFE, control_type=0x01, data=data)
        assert response.positive
        # Send tester present for 60 seconds to keep the routine running
        for i in range(60):
            response = client.tester_present()
            time.sleep(1)
        response = client.get_routine_result(0xDFFE)

        # Assert
        assert response.positive
        decode_raw_can_data(
            response.service_data.routine_status_record.decode("ascii"),
            HAPPY_PATH_TEST_FILE + ".json",
        )


def test_when_routine_control_dffe_over_70s_then_only_newest_60s_data(doip_client):
    # Test routine control with 20 CAN IDs 60 seconds
    # But send tester request after 70 seconds
    # Expect to get 60 seconds of raw CAN data

    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.change_session(0x03)
        assert response.positive
        response = client.unlock_security_access(0x03)
        assert response.positive

        # Act
        response = client.routine_control(0xDFFE, control_type=0x01, data=data)
        assert response.positive
        # Send tester present for 70 seconds to keep the routine running
        for i in range(70):
            response = client.tester_present()
            time.sleep(1)
        response = client.get_routine_result(0xDFFE)

        # Assert
        assert response.positive
        decode_raw_can_data(
            response.service_data.routine_status_record.decode("ascii"),
            KEEP_NEWEST_TEST_FILE + ".json",
        )


def test_when_routine_control_dffe_resubscribe_then_correct_result(doip_client):
    # Test routine control could be resubscribed
    # First routine control with 2 CAN IDs 60 seconds
    # Then stop routine control
    # Then start routine control with 20 CAN IDs 60 seconds
    # Expect to get 60 seconds of raw CAN data

    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.change_session(0x03)
        assert response.positive
        response = client.unlock_security_access(0x03)
        assert response.positive
        # Start routine control, Read raw CAN data for 30 seconds and 2 CAN IDs 0x154 and 0x116
        short_data = bytes(
            [0x02, 0x1E, 0x01, 0x00, 0x00, 0x01, 0x54, 0x02, 0x00, 0x00, 0x01, 0x16]
        )
        short_data += bytes([0x00] * (102 - len(short_data)))
        response = client.routine_control(0xDFFE, control_type=0x01, data=short_data)
        assert response.positive
        response = client.stop_routine(0xDFFE)
        assert response.positive
        # Start routine control, Read raw CAN data for 30 seconds and 20 CAN IDs
        response = client.routine_control(0xDFFE, control_type=0x01, data=data)
        assert response.positive
        # Send tester present for 60 seconds to keep the routine running
        for i in range(60):
            response = client.tester_present()
            time.sleep(1)
        # Send request routine result
        response = client.get_routine_result(0xDFFE)
        assert response.positive
        decode_raw_can_data(
            response.service_data.routine_status_record.decode("ascii"),
            RESUBSCRIBE_TEST_FILE + ".json",
        )


def test_when_routine_control_dffe_s3_timeout_then_negative_response(doip_client):
    # Test routine control will timeout after 5 seconds

    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.change_session(0x03)
        assert response.positive
        response = client.unlock_security_access(0x03)
        assert response.positive

        # Act
        # Read raw CAN data for 30 seconds and 20 CAN IDs
        response = client.routine_control(0xDFFE, control_type=0x01, data=data)
        assert response.positive
        # Sleep for 6 seconds
        time.sleep(6)
        response = client.get_routine_result(0xDFFE)

        # Assert
        # Expect to get negative response
        assert not response.positive


# The purpose of the overnight tests is to continuously send raw CAN data from the
# ECU using the CAN ID 777. The data will roll through a sequence of values, starting
# from 0, incrementing to 255, and then looping back to 0. This loop ensures that
# the CAN bus remains active with a steady stream of data throughout the test period.
#
# ID=777
# DATA=00000000000000
# while true; do
#   cansend vcan5 ${ID}#$(printf "%02X" $DATA)00000000000000
#   DATA=$(( (DATA + 1) % 256 ))
#   usleep 10000
# done


def test_when_routine_control_dffe_run_over_8_hours_then_correct_result(doip_client):
    # Test routine control with 20 CAN IDs 60 seconds
    # But send request result after 60 seconds
    # This test will run over night keep the routine running for 8 hours

    # Arrange
    pytest.mark.skipif(
        not OVERNIGHT_TEST,
        reason="Skip over night test, because it will take long time",
    )
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.change_session(0x03)
        assert response.positive
        response = client.unlock_security_access(0x03)
        assert response.positive

        # Act
        response = client.routine_control(0xDFFE, control_type=0x01, data=data)
        assert response.positive
        for i in range(8 * 60):
            file_name = OVERNIGHT_TEST_FILE + str(1) + f"_{i}.json"
            # Send tester present for 60 seconds to keep the routine running
            for i in range(60):
                response = client.tester_present()
                time.sleep(1)
            # Send request routine result
            response = client.get_routine_result(0xDFFE)

            # Assert
            assert response.positive
            decode_raw_can_data(
                response.service_data.routine_status_record.decode("ascii"), file_name
            )


def test_when_routine_control_dffe_resubscribe_over_8_hours_then_correct_result(
    doip_client,
):
    # Test routine control with 20 CAN IDs 60 seconds
    # But send request result and stop routine after 60 seconds
    # And then start the routine control again
    # This test will run over night keep the routine running for 8 hours

    # Arrange
    pytest.mark.skipif(
        not OVERNIGHT_TEST,
        reason="Skip over night test, because it will take long time",
    )
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)

    assert connection.is_open()
    with Client(connection, config=client_config()) as client:
        response = client.change_session(0x03)
        assert response.positive
        response = client.unlock_security_access(0x03)
        assert response.positive

        # Act
        response = client.routine_control(0xDFFE, control_type=0x01, data=data)
        assert response.positive
        for i in range(8 * 60):
            file_name = OVERNIGHT_TEST_FILE + str(2) + f"_{i}.json"
            # Send tester present for 60 seconds to keep the routine running
            for i in range(60):
                response = client.tester_present()
                time.sleep(1)
            response = client.get_routine_result(0xDFFE)

            # Assert
            assert response.positive
            decode_raw_can_data(
                response.service_data.routine_status_record.decode("ascii"), file_name
            )
            response = client.stop_routine(0xDFFE)
            assert response.positive
            response = client.routine_control(0xDFFE, control_type=0x01, data=data)
            assert response.positive


def check_signal_continuity(file_name):

    def transform_bytes_to_decimal(data):
        # The raw CAN data is represented as a hexadecimal string.
        # The last two bytes of the data represent the CAN data.
        # For example: 0xEF00000000000000
        bytes_str = data[2:4]
        value = int(bytes_str, 16)
        return value

    # Check if the signal is continuous
    # By parsing the raw CAN data and check if the data is continuous
    # If not, print the CAN ID and the timestamp

    with open(file_name, "r") as f:
        data = json.load(f)
    data = [d for d in data if d["CAN_ID"] == "0x00000777"]
    prev_value = 0
    for i in range(len(data) - 1):
        prev_index = 0
        if i == 0:
            prev_value = transform_bytes_to_decimal(data[i]["CAN_Data"])
        else:
            value = transform_bytes_to_decimal(data[i]["CAN_Data"])
            if value - prev_value != 1 and prev_value - value != 255:
                print(f"CAN ID: {data[i]['CAN_ID']}, Timestamp: {data[i]['Timestamp']}")
                print(f"Value: {value}, Previous Value:  {prev_value}")
            prev_value = value


def when_over_night_done_then_check_data():
    # Arrange
    pytest.mark.skipif(
        not OVERNIGHT_TEST,
        reason="Skip over night test, because it will take long time",
    )
    path = os.getcwd()
    file_list = os.listdir(path)

    # Act
    for file_name in file_list:
        if OVERNIGHT_TEST_FILE in file_name:
            file_name = path + "/" + file_name
            print(file_name)
            # Assert
            check_signal_continuity(file_name)
