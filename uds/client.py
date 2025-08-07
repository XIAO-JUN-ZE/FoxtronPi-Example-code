from enum import IntEnum
from uds import ffi
from typing import Dict, Callable, Optional, Any, List, Union
import ctypes
import math

MODEL_D31L = ffi.MODEL_D31L
MODEL_D31F25 = ffi.MODEL_D31F25
MODEL_D31L24 = ffi.MODEL_D31L24
MODEL_D21L = ffi.MODEL_D21L
MODEL_D31H = ffi.MODEL_D31H
MODEL_D31X = ffi.MODEL_D31X

FFIAppCategory = ffi.FFIAppCategory
FFIDidListEntry = ffi.FFIDidListEntry
FFIError = ffi.FFIError


class ActivationType(IntEnum):
    """See Table 47 - Routing activation request activation types"""

    Default = 0x00
    DiagnosticRequiredByRegulation = 0x01
    CentralSecurity = 0xE0
    OtaMode = 0xE1


def decrypt_seed_with_model(
    model: int,
) -> Callable[[int, bytes, Optional[Any]], bytes]:
    """Returns a function that decrypts a seed for the provided model.

    :param model: The car model.
    """

    def decrypt_seed(level: int, seed: bytes, params: Optional[Any] = None) -> bytes:
        """Decrypt a seed.

        :param level: The security level.
        :param seed: The seed to decrypt.

        :raises Exception: If the seed could not be decrypted.
        """
        retseed = bytearray()

        def ret(s: ffi.Sliceu8) -> None:
            retseed.extend(s.bytearray())

        array_type = ctypes.c_uint8 * len(seed)
        seed = array_type(*seed)
        ffi._errcheck(
            ffi.decrypt_seed(level, model, seed, ret),
            ffi.FFIError.Ok,
        )
        return bytes(retseed)

    return decrypt_seed


class DoIPClient:
    """A DoIPClient instance."""

    def __init__(
        self,
        target_ip_address: str,
        target_logical_address: int,
        source_logical_address: int = 0x0E00,
        request_activation=True,
        activation_type=ActivationType.Default,
    ):
        """Create a new instance of DoIPClient.

        :param source_logical_address: The logical address of the client.
        :param target_ip_address: The IP address of the server.
        :param target_logical_address: The logical address of the server.

        :raises Exception: If the client could not be created.
        """
        target_ip_address_bytes = bytes(target_ip_address, "ascii")
        # Initialize to a null pointer. The FFI function will fill this.
        self._client_ptr = ctypes.c_void_p()
        ffi._errcheck(
            ffi.doipclient_connect(
                ctypes.byref(self._client_ptr),  # Pass by reference
                source_logical_address,
                target_ip_address_bytes,
                target_logical_address,
            ),
            ffi.FFIError.Ok,
        )
        if request_activation:
            ffi._errcheck(
                ffi.doipclient_request_activation(self._client_ptr, activation_type),
                ffi.FFIError.Ok,
            )

    def close(self):
        """Explicitly close the DoIPClient instance and release resources."""
        if self._client_ptr:
            ffi._errcheck(
                ffi.doipclient_drop(ctypes.byref(self._client_ptr)), ffi.FFIError.Ok
            )
            self._client_ptr = None  # Mark as closed to prevent double-free

    def __del__(self):
        """Drop the DoIPClient instance when garbage collected."""
        self.close()

    def is_open(self) -> bool:
        """Check if the DoIPClient instance is open.

        :return: True if the DoIPClient instance is open.
        :rtype: bool
        """
        return self._client_ptr is not None and ffi.doipclient_is_open(self._client_ptr)

    def send_diagnostic(self, payload: bytes, timeout: Optional[float] = None):
        """Send a diagnostic request.

        This function will not timeout if the timeout value is None or infinity or NaN.

        :param payload: The payload of the diagnostic request.
        :param timeout: The unit of timeout is seconds.

        :raises Exception: If the request could not be sent.
        """
        if self._client_ptr is None:
            raise RuntimeError("DoIPClient is closed.")
        if timeout is None or not math.isfinite(timeout):
            timeout = float("inf")

        payload_bytearray = bytearray(payload)
        payload_ctype_array = (ctypes.c_uint8 * len(payload_bytearray)).from_buffer(
            payload_bytearray
        )

        res = ffi.doipclient_send_diagnostic(
            self._client_ptr, payload_ctype_array, timeout
        )
        ffi._errcheck(
            res,
            ffi.FFIError.Ok,
        )

    def receive_diagnostic(self, timeout: Optional[float] = None) -> bytes:
        """Receive a diagnostic response.

        This function will not timeout if the timeout value is None, infinity or NaN.

        :param timeout: The unit of timeout is seconds.

        :raises Exception: If the response could not be received.
        """
        if self._client_ptr is None:
            raise RuntimeError("DoIPClient is closed.")
        if timeout is None or not math.isfinite(timeout):
            timeout = float("inf")

        msg = bytearray()

        def retmsg(s: ffi.Sliceu8) -> None:
            msg.extend(s.bytearray())

        ffi._errcheck(
            ffi.doipclient_receive_diagnostic(self._client_ptr, timeout, retmsg),
            ffi.FFIError.Ok,
        )
        return bytes(msg)

    def receive_multiple_diagnostic_responses(
        self, timeout: Optional[float] = None
    ) -> List[bytes]:
        """Receive multiple diagnostic responses, e.g., from a functional request.

        This function collects responses for the specified duration. A finite,
        non-negative timeout is required.

        :param timeout: The duration in seconds to collect responses.

        :return: A list of byte arrays, where each is a complete DoIP message payload.
        :rtype: List[bytes]

        :raises ValueError: If the timeout is None or not a finite, non-negative number.
        :raises Exception: If the FFI call returns an error.
        """
        if self._client_ptr is None:
            raise RuntimeError("DoIPClient is closed.")
        if (
            timeout is None
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout < 0
        ):
            raise ValueError(
                "A finite, non-negative timeout must be provided for receive_multiple_diagnostic_responses"
            )

        messages = []

        def retmsg(s: ffi.Sliceu8) -> None:
            messages.append(bytes(s.bytearray()))

        ffi._errcheck(
            ffi.doipclient_receive_multiple_diagnostic_responses(
                self._client_ptr, timeout, retmsg
            ),
            ffi.FFIError.Ok,
        )
        return messages

    def set_target_address(self, new_target_address: int):
        """Change the target logical address.

        :param new_target_address: The new target logical address.

        :raises Exception: If the target address could not be changed.
        """
        if self._client_ptr is None:
            raise RuntimeError("DoIPClient is closed.")
        ffi._errcheck(
            ffi.doipclient_set_target_address(self._client_ptr, new_target_address),
            ffi.FFIError.Ok,
        )


def get_dids_by_app_category(
    app_category: Union[int, FFIAppCategory],
) -> List[FFIDidListEntry]:
    """
    Retrieves a list of DIDs filtered by the specified application category.

    :param app_category: The FFIAppCategory enum member (e.g., ffi.FFIAppCategory.FdA53)
                         or its underlying integer value.
    :return: A list of FFIDidListEntry objects.
    :raises Exception: If the FFI call returns an error.
    """
    received_dids: List[FFIDidListEntry] = []

    def did_list_callback(entries: ffi.SliceFFIDidListEntry) -> None:
        """Callback to receive the list of DIDs from the FFI layer."""
        for i in range(entries.len):
            # Create a new FFIDidListEntry and copy data
            # to ensure it's owned by Python and lives beyond the callback.
            entry_data = entries[i]
            copied_entry = FFIDidListEntry(
                did=entry_data.did, app_category=entry_data.app_category
            )
            received_dids.append(copied_entry)

    ffi._errcheck(
        ffi.get_dids_by_app_category(app_category, did_list_callback),
        ffi.FFIError.Ok,
    )
    return received_dids
