from doipclient import DoIPClient


FDC_LOGICAL_ADDRESS = 0x680


# Test 7.4 APP vehicle identification and announcement request message
# Vehicle announcement
# The table 5 defines the vehicle announcement message
# def test_when_activation_line_is_up_then_receive_vehicle_announcement():
#     # Arrange
#     source_interface = "eth0"

#     # Act
#     address, annountment = DoIPClient.await_vehicle_announcement(source_interface)
#     ip, address = address

#     # Assert
#     assert len(annountment.vin) == 17
#     assert annountment.logical_address == FDC_LOGICAL_ADDRESS
#     assert len(annountment.eid) == 6
#     assert len(annountment.gid) == 6


# Test 7.4 APP vehicle identification and announcement request message
# Vehicle Identification with no message parameters
# The table 5 defines the vehicle identification response message
def test_when_send_vehicle_identification_then_receive_vehicle_identification():
    # Arrange
    client = DoIPClient

    # Act
    address, response = DoIPClient.get_entity()

    # Assert
    assert len(response.vin) == 17
    assert response.logical_address == FDC_LOGICAL_ADDRESS
    assert len(response.eid) == 6
    assert len(response.gid) == 6
    assert response.further_action_required == False


# Test 7.4 APP vehicle identification and announcement request message
# Vehicle Identification with vin
# The table 5 defines the vehicle identification response message
def test_when_send_vehicle_identification_then_receive_vehicle_identification():
    # Arrange
    client = DoIPClient

    vin = "RF5D31LHT00ET4028"

    # Act
    address, response = DoIPClient.get_entity(vin)

    # Assert
    assert len(response.vin) == 17
    assert response.logical_address == FDC_LOGICAL_ADDRESS
    assert len(response.eid) == 6
    assert len(response.gid) == 6
    assert response.further_action_required == False


# Test 7.5 APP diagnostic power mode information request and response
def test_when_send_diagnostic_power_mode_then_receive_diagnostic_power_mode():
    # Arrange
    client = DoIPClient

    # Act
    response = DoIPClient.request_diagnostic_power_mode()

    # Assert
    assert response.power_mode_status == 0x02  # not supported
