from uds.client import DoIPClient, ActivationType
from doipclient import DoIPClient as pyDoIPClient
from uds.config import DOIP_SERVER_IP
import pytest


@pytest.fixture(scope="module")
def doip_client(request):
    address, response = pyDoIPClient.get_entity(
        protocol_version=0xFF, ecu_ip_address=DOIP_SERVER_IP
    )
    print(
        f"Found DoIP entity at {address} with logical address {response.logical_address}"
    )
    # The type of address is a tuple, and the DoIPClient expects a string with the IP address
    # So we convert the tuple to a string and extract the IP address
    target_ip = str(address[0])
    target_logical_address = response.logical_address

    # Determine activation type based on test marker
    activation_type = ActivationType.Default
    if request.node.get_closest_marker("regulated_doip"):
        activation_type = ActivationType.DiagnosticRequiredByRegulation
        print(f"Using activation type: {activation_type.name} ({activation_type.value:#04x})")
    else:
        print(f"Using activation type: {activation_type.name} ({activation_type.value:#04x})")

    client = DoIPClient(target_ip, target_logical_address, activation_type=activation_type)
    assert client.is_open()

    yield client

    client.close()
