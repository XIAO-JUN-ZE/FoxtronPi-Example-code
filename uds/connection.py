from typing import Optional
from uds.client import DoIPClient
from udsoncan.connections import BaseConnection


class DoIPConnection(BaseConnection):
    def __init__(self, doip_client: DoIPClient, name: Optional[str] = None):
        BaseConnection.__init__(self, name)
        self.doip_client = doip_client

    def specific_send(self, payload):
        self.doip_client.send_diagnostic(payload, 2)

    def specific_wait_frame(self, timeout=2):
        msg = self.doip_client.receive_diagnostic(timeout)
        # 12 bytes include 8 bytes header and source and target address
        # [version | inverse of version | payload length | source address | target address | user data]
        return msg[12:]

    def open(self):
        pass

    def close(self):
        pass

    def empty_rxqueue(self):
        pass

    def is_open(self) -> bool:
        return self.doip_client.is_open()
