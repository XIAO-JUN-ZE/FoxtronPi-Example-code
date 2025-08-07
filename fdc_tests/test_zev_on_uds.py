from uds.connection import DoIPConnection
from uds.client_config import client_config
import udsoncan
import datetime
import time
import struct
from udsoncan.client import Client
from udsoncan.services import *
from udsoncan.common.dtc import Dtc
import pytest  # Added import for pytest
from uds.client import (
    get_dids_by_app_category,
    FFIAppCategory,
)  # Import FFIAppCategory from client


def debug_print(msg):
    print(f"{datetime.datetime.now()}: {msg}")


@pytest.fixture(scope="module")
def ensure_zev_dids():
    """Fixture to ensure ZEV DIDs are available, otherwise skips tests."""
    try:
        zev_dids_entries = get_dids_by_app_category(FFIAppCategory.Zev)
    except AttributeError:
        pytest.skip(
            "FFIAppCategory.Zev is not defined in ffi bindings. Skipping ZEV-related tests."
        )
    if not zev_dids_entries:
        pytest.skip("ZEV DID category is empty. Skipping ZEV-related tests.")
    return zev_dids_entries


# Test 6.1 DTCStatusMask/DTC Status Byte and DTCStatusAvailabilityMask and
# table 2 DTC status bits definition in J1939-3
@pytest.mark.regulated_doip
def test_when_perform_read_dtc_information_request_then_check_status_availability_mask(
    doip_client, ensure_zev_dids
):
    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()
    with Client(connection, config=client_config()) as client:

        # Act
        response = client.get_supported_dtc()
        assert response.positive

        # Assert
        assert response.service_data.status_availability.test_failed
        assert (
            response.service_data.status_availability.test_failed_this_operation_cycle
        )
        assert response.service_data.status_availability.pending
        assert response.service_data.status_availability.confirmed
        assert (
            response.service_data.status_availability.test_not_completed_since_last_clear
        )
        assert (
            response.service_data.status_availability.test_not_completed_this_operation_cycle
        )


# Test 6.2 DTCSeverityMask and DTCSeverityAvailabilityMask
# DTC serverity and DTC class bits definition in J1939-3 table 4
# Test 6.3 FunctionalGroupIdentifier
@pytest.mark.regulated_doip
# Test 6.5 DTC Format Identifier is SAE_J2012_DTCFormat 0x04
def test_when_perform_read_dtc_information_request_with_severity_mask_then_receive_positive_response(
    doip_client, ensure_zev_dids
):
    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()

    with Client(connection, config=client_config()) as client:
        # Act
        # SID 0x19, Subfunction reportWWHOBDDTCByMaskRecord (0x42)
        # Parameters:
        # FunctionalGroupIdentifier: ZEV propulsion group (0x33)
        # DTC status mask: 0x5F
        # DTC severity mask (combined with class): 0x02 (Maintenance Only for J1939-73)

        response = client.get_wwh_obd_dtc_by_status_mask(
            functional_group_id=0x33,
            status_mask=0x5F,
            severity_mask=0x00,  # Severity part of the original combined 0x02 byte
            dtc_class=0x02,  # Class part of the original combined 0x02 byte
        )

        # Assert
        assert response.positive
        assert (
            response.service_data.subfunction_echo
            == ReadDTCInformation.Subfunction.reportWWHOBDDTCByMaskRecord
        )
        assert response.service_data.functional_group_id == 0x33
        assert response.service_data.status_availability.get_byte_as_int() == 0x5F
        assert response.service_data.severity_availability.get_byte_as_int() == 0xE0

        # Check DTCSeverityAvailabilityMask direclty because service_data.severity_availability does not have DTC class information
        assert response.data[3] == 0xE2

        # Check DTCFormatIdentifier - For WWH-OBD, this should be SAE_J2012_DA_DTCFormat_04
        assert (
            response.service_data.dtc_format == Dtc.Format.SAE_J2012_DA_DTCFormat_04
        )  # J1939-73 DTC format


# Test 6.4 GroupOfDTCIdentifier ZEV propulsion FFFF33 and all groups FFFFFF
def test_when_perform_clear_dtc_with_group_of_dtc_identifier_ffff33_then_receive_positive_response(
    doip_client, ensure_zev_dids
    doip_client, ensure_zev_dids
):
    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()

    with Client(connection, config=client_config()) as client:
        # Act
        response = client.clear_dtc(0xFFFF33)
        # Assert
        assert response.positive


# Test 6.6.1  Protocol Detection
# There are two ways to detect the protocol and we will use the second one
# This test is to check the step b
@pytest.mark.regulated_doip
def test_when_perform_functional_request_of_did_0xf810_then_receive_positive_response(
    doip_client, ensure_zev_dids
):
    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()

    with Client(connection, config=client_config()) as client:

        # Act
        connection.doip_client.set_target_address(0xE000)
        response = client.read_data_by_identifier(0xF810)
        connection.doip_client.set_target_address(0x0680)

        # Assert
        assert response.positive


# Test 6.6.1  Protocol Detection
# There are two ways to detect the protocol and we will use the second one
# This test is to check the step c
@pytest.mark.regulated_doip
def test_when_perform_functional_request_of_did_0xf41c_then_receive_positive_response(
    doip_client, ensure_zev_dids
):
    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()

    with Client(connection, config=client_config()) as client:
        connection.doip_client.set_target_address(0xE000)
        response = client.read_data_by_identifier(0xF810)
        connection.doip_client.set_target_address(0x0680)
        assert response.positive

        # Act
        response = client.read_data_by_identifier(0xF41C)

        # Assert
        assert response.positive


# Test 6.7.5 Maximum Message length
# Test 8.3.2.1 Up to 6 DIDs can be requested in a single request
# Note: We allow at least 6 DIDs be requested
@pytest.mark.regulated_doip
def test_when_perform_read_did_request_with_6_dids_then_receive_positive_response(
    doip_client, ensure_zev_dids
):
    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()

    did_list = [0xF810, 0xF41C, 0xF41F, 0xF420, 0xF421, 0xF430]
    with Client(connection, config=client_config()) as client:
        # Act
        response = client.read_data_by_identifier(did_list)

        # Assert
        assert response.positive is True


# Test 7.1.2 Request supported DIDs from Vehicle
# Test range of supported DIDs 0xF400 to 0xF4FF
# A range is defined as a block of 32 DIDs
@pytest.mark.regulated_doip
def test_when_perform_read_supported_dids_request_with_range_F4XX_then_receive_positive_response(
    doip_client, ensure_zev_dids
):
    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()

    did_range_list = [0xF400, 0xF420, 0xF440, 0xF460, 0xF480, 0xF4A0, 0xF4C0, 0xF4E0]
    did_result_list = []

    with Client(connection, config=client_config()) as client:
        # Act
        for did in did_range_list:
            response = client.read_data_by_identifier(did)
            # Save all response
            did_result_list.append(response)

        # Assert
        # Check if the last byte of the payload is 0x00 then
        # the next DID should not be supported
        for i in range(len(did_range_list) - 1):
            if did_result_list[i].positive:
                # Check the payload length equals to 7
                assert len(did_result_list[i].get_payload()) == 7
                # Check the bit map of the supported DIDs
                # If the 32nd bit is 0 then the next result shoud not be positive
                if did_result_list[i].get_payload()[-1] & 0x01 == 0:
                    assert did_result_list[i + 1].positive is False
                else:
                    assert did_result_list[i + 1].positive


@pytest.mark.regulated_doip
def test_read_all_dids_in_zev_category(doip_client, ensure_zev_dids):
    zev_dids_entries = ensure_zev_dids  # Get DIDs from fixture
    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()

    with Client(connection, config=client_config()) as client:
        assert len(zev_dids_entries) > 0

        for did_entry in zev_dids_entries:
            debug_print(f"Reading DID: {hex(did_entry.did)} from ZEV category")
            response = client.read_data_by_identifier(did_entry.did)
            # Assert
            assert response.positive, f"Failed to read DID {hex(did_entry.did)}"
            debug_print(
                f"Successfully read DID: {hex(did_entry.did)}, Value: {response.service_data.values[did_entry.did]}"
            )


# Test 7.1.2 Request supported DIDs from Vehicle
# Test range of supported DIDs 0xF800 to 0xF8FF
# A range is defined as a block of 32 DIDs
@pytest.mark.regulated_doip
def test_when_perform_read_supported_dids_request_with_range_F8XX_then_receive_positive_response(
    doip_client, ensure_zev_dids
):
    # Arrange
    assert doip_client.is_open()
    udsoncan.setup_logging()
    connection = DoIPConnection(doip_client)
    assert connection.is_open()

    did_range_list = [0xF800, 0xF820, 0xF840, 0xF860, 0xF880, 0xF8A0, 0xF8C0, 0xF8E0]
    did_result_list = []

    with Client(connection, config=client_config()) as client:
        # Act
        for did in did_range_list:
            response = client.read_data_by_identifier(did)
            # Save all response
            did_result_list.append(response)

        # Assert
        # Check if the last byte of the payload is 0x00 then
        # the next DID should not be supported
        for i in range(len(did_range_list) - 1):
            if did_result_list[i].positive:
                # Check the payload length equals to 7
                assert len(did_result_list[i].get_payload()) == 7
                # Check the bit map of the supported DIDs
                # If the 32nd bit is 0 then the next result shoud not be positive
                if did_result_list[i].get_payload()[-1] & 0x01 == 0:
                    assert did_result_list[i + 1].positive is False
                else:
                    assert did_result_list[i + 1].positive
