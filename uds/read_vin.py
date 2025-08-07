from uds.client import DoIPClient
from uds.connection import DoIPConnection as DoIPClientUDSConnector
from uds.client_config import client_config
from uds.config import DOIP_SERVER_IP, DOIP_DEFAULT_LOGICAL_ADDRESS
from udsoncan.client import Client
from udsoncan.services import *
import datetime
import os


def debug_print(msg):
    print(f"{datetime.datetime.now()}: {msg}")


os.environ["RUST_LOG"] = "trace"

doip_client = DoIPClient(DOIP_SERVER_IP, DOIP_DEFAULT_LOGICAL_ADDRESS)
uds_connection = DoIPClientUDSConnector(doip_client)
assert uds_connection.is_open
with Client(uds_connection, request_timeout=4, config=client_config()) as client:
    DID = int("0x"+input("Please input DID Number:"),16)
    print(type(DID))
    response = client.read_data_by_identifier(DID) # 0xF190
    debug_print(f"VIN: {response.service_data.values[DID]}")
