"""Configuration values for UDS connections."""

import os

# DoIP server configuration - can be overridden with environment variables
DOIP_SERVER_IP = os.environ.get("DOIP_SERVER_IP", "192.168.200.1") #FD gen2 IP 169.254.200.1 , gen1(Foxpi) IP = 192.168.200.1
DOIP_DEFAULT_LOGICAL_ADDRESS = int(os.environ.get("DOIP_LOGICAL_ADDRESS", "0x0680"), 16)
