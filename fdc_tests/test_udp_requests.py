from doipclient import DoIPClient
from uds.config import DOIP_SERVER_IP, DOIP_DEFAULT_LOGICAL_ADDRESS


def test_when_get_identity_with_default_protocol_version_then_return_vin_logical_address_and_fxn_001():
    # Act
    address, announcement = DoIPClient.get_entity(
        ecu_ip_address=DOIP_SERVER_IP, protocol_version=0xFF
    )
    vin = announcement.vin
    logical_address = announcement.logical_address
    eid = announcement.eid
    gid = announcement.gid
    further_action = announcement.further_action_required
    vin_gid_sync_status = announcement.vin_sync_status

    # Assert
    # note: the EID is not tested here, as it is an EMAC address and is not constant
    assert len(vin) == 17
    assert logical_address == DOIP_DEFAULT_LOGICAL_ADDRESS
    assert len(eid) == 6
    assert eid != b"\x00\x00\x00\x00\x00\x00"
    assert eid != b"\xff\xff\xff\xff\xff\xff"
    assert len(gid) == 6
    assert gid != b"\x00\x00\x00\x00\x00\x00"
    assert gid == b"\xff\xff\xff\xff\xff\xff"
    assert further_action == 0x00
    assert vin_gid_sync_status == 0x00


def test_when_get_identity_with_protocol_version_03_then_return_vin_logical_address_and_fxn_001():
    # Act
    address, announcement = DoIPClient.get_entity(
        ecu_ip_address=DOIP_SERVER_IP, protocol_version=3
    )
    vin = announcement.vin
    logical_address = announcement.logical_address
    eid = announcement.eid
    gid = announcement.gid
    further_action = announcement.further_action_required
    vin_gid_sync_status = announcement.vin_sync_status

    # Assert
    # note: the EID is not tested here, as it is an EMAC address and is not constant
    assert len(vin) == 17
    assert logical_address == DOIP_DEFAULT_LOGICAL_ADDRESS
    assert len(eid) == 6
    assert eid != b"\x00\x00\x00\x00\x00\x00"
    assert eid != b"\xff\xff\xff\xff\xff\xff"
    assert len(gid) == 6
    assert gid != b"\x00\x00\x00\x00\x00\x00"
    assert gid == b"\xff\xff\xff\xff\xff\xff"
    assert further_action == 0x00
    assert vin_gid_sync_status == 0x00


# TODO: implement this test
# def test_when_get_entity_with_same_vin_then_return_vin_logical_address_and_fxn_001():
#     # Act
#     address, announcement = DoIPClient.get_entity(vin="RF5D31LHT00ET4028")
#     vin = announcement.vin
#     logical_address = announcement.logical_address
#     gid = announcement.gid
#     further_action = announcement.further_action_required
#     vin_gid_sync_status = announcement.vin_gid_sync_status

#     # Assert
#     # note: the EID is not tested here, as it is an EMAC address and is not constant
#     assert vin == "RF5D31LHT00ET4028"
#     assert logical_address == DOIP_DEFAULT_LOGICAL_ADDRESS
#     assert gid == 0x00
#     assert further_action == 0x00
#     assert vin_gid_sync_status == 0x00

# TODO: implement this test
# def test_when_get_entity_with_different_vin_then_timeout():
#     # Act
#     address, announcement = DoIPClient.get_entity(vin="RF5D31LHT00ET4029")

#     # Assert
#     assert announcement is None

# TODO: implement this test
# def test_when_get_identity_with_protocol_2_then_return_incorrect_pattern_format():
#     # Act
#     address, announcement = DoIPClient.get_entity()
