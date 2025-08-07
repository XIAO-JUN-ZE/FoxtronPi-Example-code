from __future__ import annotations
import ctypes
import typing

T = typing.TypeVar("T")
c_lib = None

def init_lib(path):
    """Initializes the native library. Must be called at least once before anything else."""
    global c_lib
    c_lib = ctypes.cdll.LoadLibrary(path)

    c_lib.doipclient_init.argtypes = []
    c_lib.doipclient_connect.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint16, ctypes.POINTER(ctypes.c_char), ctypes.c_uint16]
    c_lib.doipclient_drop.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
    c_lib.doipclient_is_open.argtypes = [ctypes.c_void_p]
    c_lib.doipclient_request_activation.argtypes = [ctypes.c_void_p, ctypes.c_uint8]
    c_lib.doipclient_send_diagnostic.argtypes = [ctypes.c_void_p, Sliceu8, ctypes.c_double]
    c_lib.doipclient_receive_diagnostic.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.CFUNCTYPE(None, Sliceu8)]
    c_lib.doipclient_receive_multiple_diagnostic_responses.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.CFUNCTYPE(None, Sliceu8)]
    c_lib.decrypt_seed.argtypes = [ctypes.c_uint8, ctypes.c_uint8, Sliceu8, ctypes.CFUNCTYPE(None, Sliceu8)]
    c_lib.doipclient_set_target_address.argtypes = [ctypes.c_void_p, ctypes.c_uint16]
    c_lib.get_dids_by_app_category.argtypes = [ctypes.c_uint8, ctypes.CFUNCTYPE(None, SliceFFIDidListEntry)]

    c_lib.doipclient_connect.restype = ctypes.c_int
    c_lib.doipclient_drop.restype = ctypes.c_int
    c_lib.doipclient_is_open.restype = ctypes.c_bool
    c_lib.doipclient_request_activation.restype = ctypes.c_int
    c_lib.doipclient_send_diagnostic.restype = ctypes.c_int
    c_lib.doipclient_receive_diagnostic.restype = ctypes.c_int
    c_lib.doipclient_receive_multiple_diagnostic_responses.restype = ctypes.c_int
    c_lib.decrypt_seed.restype = ctypes.c_int
    c_lib.doipclient_set_target_address.restype = ctypes.c_int
    c_lib.get_dids_by_app_category.restype = ctypes.c_int



def doipclient_init():
    """ This should typically be called once at the start of the application.
 It's safe to call multiple times, but subsequent calls will have no effect."""
    return c_lib.doipclient_init()

def doipclient_connect(client_ptr: ctypes.POINTER(ctypes.c_void_p), source_logical_address: int, target_ip_address: bytes, target_logical_address: int) -> ctypes.c_int:
    """ Creates a new DoIP client instance and establishes a connection.

 This function spawns a background thread to handle the asynchronous DoIP communication.

 # Arguments
 * `client_ptr` - A pointer to a `*mut DoIPClient`. On success (`FFIError::Ok`),
   this location will be updated to hold the pointer to the newly created client instance.
   The caller *must* initialize the variable pointed to by `client_ptr` to `null`
   before calling this function to avoid memory leaks.
 * `source_logical_address` - The logical address for this client (tester), typically in the range 0x0E00-0x0FFF.
 * `target_ip_address` - An ASCII string representing the IP address of the DoIP gateway/ECU.
 * `target_logical_address` - The initial logical address of the target ECU.

 # Returns
 * `FFIError::Ok` on success. The `client_ptr` location will contain the client handle.
 * `FFIError::NullPointerPassed` if `client_ptr` is null.
 * `FFIError::InvalidArgument` if `target_ip_address` is not a valid IP address string,
   or if `source_logical_address` is invalid.
 * `FFIError::ConnectFailed` if the underlying TCP connection fails or the background thread cannot be started.
 * Other `FFIError` variants for internal errors.

 # Safety
 The caller is responsible for calling `doipclient_drop` on the returned client pointer
 to release resources when done. The `client_ptr` argument must point to a valid mutable
 location capable of holding a `*mut DoIPClient`."""
    if not hasattr(target_ip_address, "__ctypes_from_outparam__"):
        target_ip_address = ctypes.cast(target_ip_address, ctypes.POINTER(ctypes.c_char))
    return c_lib.doipclient_connect(client_ptr, source_logical_address, target_ip_address, target_logical_address)

def doipclient_drop(client_ptr: ctypes.POINTER(ctypes.c_void_p)) -> ctypes.c_int:
    """ Destroys a DoIP client instance and cleans up associated resources.

 This function signals the background thread to shut down and waits for it to complete
 before freeing the memory associated with the client handle.

 # Arguments
 * `client_ptr` - A pointer to the `*mut DoIPClient` variable holding the client handle
   obtained from `doipclient_connect`.

 # Returns
 * `FFIError::Ok` on success.
 * `FFIError::NullPointerPassed` if `client_ptr` is null.

 # Safety
 * The pointer `*client_ptr` must be a valid pointer obtained from `doipclient_connect`
   that has not already been passed to `doipclient_drop`.
 * After this function returns successfully, the pointer `*client_ptr` is invalidated
   (set to null), and must not be used again.
 * Calling this function multiple times with the same valid pointer (before it's set to null)
   is safe; subsequent calls after the first successful one will do nothing."""
    return c_lib.doipclient_drop(client_ptr)

def doipclient_is_open(client: ctypes.c_void_p) -> bool:
    """ Checks if the DoIP routing is currently activated for the client.

 # Arguments
 * `client` - A pointer to the `DoIPClient` instance.

 # Returns
 * `true` if routing is activated, `false` otherwise (including if `client` is null or the lock is poisoned)."""
    return c_lib.doipclient_is_open(client)

def doipclient_request_activation(client: ctypes.c_void_p, activation_type: int) -> ctypes.c_int:
    """ Requests DoIP routing activation from the server.

 # Arguments
 * `client` - A pointer to the `DoIPClient` instance.
 * `activation_type` - The type of activation requested (e.g., 0 for default). See ISO 13400-2.

 # Returns
 * `FFIError::Ok` if activation was successful.
 * `FFIError::NullPointerPassed` if `client` is null.
 * `FFIError::RoutingActivationDenied` if the server denied the request.
 * `FFIError::ConnectFailed` if the background thread is not running.
 * Other `FFIError` variants for communication or parsing errors."""
    return c_lib.doipclient_request_activation(client, activation_type)

def doipclient_send_diagnostic(client: ctypes.c_void_p, payload: Sliceu8 | ctypes.Array[ctypes.c_uint8], timeout: float) -> ctypes.c_int:
    """ Sends a UDS diagnostic message payload over DoIP.

 This function sends the request to the background thread and waits for an
 acknowledgement (positive or negative) from the DoIP server regarding the
 transmission, *not* the diagnostic response itself. Use `doipclient_receive_diagnostic`
 to get the actual UDS response.

 # Arguments
 * `client` - A pointer to the `DoIPClient` instance.
 * `payload` - A slice containing the raw UDS message bytes (SID and parameters).
 * `timeout` - Timeout in seconds to wait for the DoIP acknowledgement (not the UDS response).
   Use `f64::INFINITY` or a negative value for no timeout.

 # Returns
 * `FFIError::Ok` if the message was acknowledged positively by the DoIP layer.
 * `FFIError::NullPointerPassed` if `client` is null.
 * `FFIError::DiagnosticMessageNegativeAck` if the DoIP layer negatively acknowledged the message.
 * `FFIError::Timeout` if the DoIP acknowledgement wasn't received within the specified timeout.
 * `FFIError::ConnectFailed` if the background thread is not running.
 * Other `FFIError` variants for communication errors."""
    if hasattr(payload, "_length_") and getattr(payload, "_type_", "") == ctypes.c_uint8:
        payload = Sliceu8(data=ctypes.cast(payload, ctypes.POINTER(ctypes.c_uint8)), len=len(payload))

    return c_lib.doipclient_send_diagnostic(client, payload, timeout)

def doipclient_receive_diagnostic(client: ctypes.c_void_p, timeout: float, retmsg) -> ctypes.c_int:
    """ Receives a UDS diagnostic message response over DoIP.

 This function waits for a diagnostic message response from the DoIP server.
 It handles DoIP Alive Checks automatically and filters messages to match the
 client's target address. It also handles UDS response pending messages internally.

 # Arguments
 * `client` - A pointer to the `DoIPClient` instance.
 * `timeout` - Timeout in seconds to wait for the diagnostic response message.
   Use `f64::INFINITY` or a negative value for potentially infinite wait (respecting UDS P2/P2* timeouts).
 * `retmsg` - A callback function (`ReturnSliceU8`) provided by the caller. If a
   diagnostic message is successfully received, this callback will be invoked with
   the full DoIP message payload (including SA, TA, and UDS data).

 # Returns
 * `FFIError::Ok` if a diagnostic message was received and passed to the `retmsg` callback.
 * `FFIError::NullPointerPassed` if `client` is null.
 * `FFIError::Timeout` if no diagnostic message was received within the specified timeout.
 * `FFIError::EOF` if the connection was closed while waiting.
 * `FFIError::ConnectFailed` if the background thread is not running.
 * `FFIError::ParseError` if the received message could not be parsed.
 * Other `FFIError` variants for communication errors.

 # Safety
 The `retmsg` callback must be a valid function pointer. The data passed to the
 callback is only valid for the duration of the callback execution."""
    if not hasattr(retmsg, "__ctypes_from_outparam__"):
        retmsg = callbacks.fn_Sliceu8(retmsg)

    return c_lib.doipclient_receive_diagnostic(client, timeout, retmsg)

def doipclient_receive_multiple_diagnostic_responses(client: ctypes.c_void_p, timeout: float, retmsg) -> ctypes.c_int:
    """ Receives multiple UDS diagnostic message responses over DoIP, typically from a functional request.

 This function waits for multiple diagnostic messages from the DoIP server. It is useful
 after sending a request to a functional address, where multiple ECUs may respond.
 The `retmsg` callback will be invoked for each diagnostic message received.

 # Arguments
 * `client` - A pointer to the `DoIPClient` instance.
 * `timeout` - Timeout in seconds for the message collection phase. The background
   thread will listen for responses for this duration.
   This FFI call itself waits for a slightly longer period (`timeout` + 2 seconds).
   This extra time acts as a buffer to ensure that all messages collected by the
   background thread can be successfully streamed back to the FFI caller without
   the caller timing out prematurely.
 * `retmsg` - A callback function (`ReturnSliceU8`) provided by the caller. This
   callback will be invoked for each diagnostic message successfully received.

 # Returns
 * `FFIError::Ok` if the collection period completed successfully. The `retmsg` callback
   will have been called zero or more times.
 * `FFIError::NullPointerPassed` if `client` is null.
 * `FFIError::Timeout` if the FFI layer times out waiting for responses from the background thread.
 * `FFIError::ConnectFailed` if the background thread is not running.
 * Other `FFIError` variants for communication or parsing errors during collection.

 # Safety
 The `retmsg` callback must be a valid function pointer. The data passed to the
 callback is only valid for the duration of the callback execution."""
    if not hasattr(retmsg, "__ctypes_from_outparam__"):
        retmsg = callbacks.fn_Sliceu8(retmsg)

    return c_lib.doipclient_receive_multiple_diagnostic_responses(client, timeout, retmsg)

def decrypt_seed(level: int, model: int, seed: Sliceu8 | ctypes.Array[ctypes.c_uint8], retseed) -> ctypes.c_int:
    """ Decrypts a UDS Security Access seed using a predefined key.

 This function implements a specific seed-key algorithm based on the security level
 and car model.

 # Arguments
 * `level` - The security access level (e.g., 1, 3, 5).
 * `model` - The car model identifier (e.g., `MODEL_D31L`).
 * `seed` - A 16-byte slice containing the seed received from the ECU.
 * `retseed` - A callback function (`ReturnSliceU8`) provided by the caller. On success,
   this callback will be invoked with the calculated 16-byte key.

 # Returns
 * `FFIError::Ok` if the key was successfully calculated and passed to the `retseed` callback.
 * `FFIError::InvalidArgument` if the `level`, `model`, or `seed` length is invalid.

 # Safety
 The `retseed` callback must be a valid function pointer. The data passed to the
 callback is only valid for the duration of the callback execution."""
    if hasattr(seed, "_length_") and getattr(seed, "_type_", "") == ctypes.c_uint8:
        seed = Sliceu8(data=ctypes.cast(seed, ctypes.POINTER(ctypes.c_uint8)), len=len(seed))

    if not hasattr(retseed, "__ctypes_from_outparam__"):
        retseed = callbacks.fn_Sliceu8(retseed)

    return c_lib.decrypt_seed(level, model, seed, retseed)

def doipclient_set_target_address(client: ctypes.c_void_p, new_target_address: int) -> ctypes.c_int:
    """ Sets the target logical address for subsequent diagnostic messages.

 This updates the target address used internally by the background thread
 when `doipclient_send_diagnostic` is called.

 # Arguments
 * `client` - A pointer to the `DoIPClient` instance.
 * `new_target_address` - The new logical address to target.

 # Returns
 * `FFIError::Ok` on success.
 * `FFIError::NullPointerPassed` if `client` is null.
 * `FFIError::ConnectFailed` if the background thread is not running."""
    return c_lib.doipclient_set_target_address(client, new_target_address)

def get_dids_by_app_category(app_category_filter_u8: int, ret_dids_callback) -> ctypes.c_int:
    """ Looks up Data Identifiers (DIDs) based on a given application category.

 This function filters a predefined list of DIDs and returns those matching
 the specified `app_category_filter` via a callback mechanism.

 # Arguments
 * `app_category_filter` - The `FFIAppCategory` to filter DIDs by.
 * `ret_dids_callback` - A callback function (`ReturnDidListEntrySlice`) provided
   by the caller. If DIDs are found, this callback will be invoked with a slice
   of `FFIDidListEntry` structures.

 # Returns
 * `FFIError::Ok` if the operation was successful (even if no DIDs are found,
   in which case the callback is invoked with an empty slice).
 * `FFIError::InternalError` if the callback invocation fails (e.g., due to a panic
   within the callback itself on the FFI caller's side, if such panics are caught
   and translated by the FFI bridge).
 * `FFIError::InvalidArgument` if the provided `app_category_filter` cannot be
   converted to an internal representation."""
    if not hasattr(ret_dids_callback, "__ctypes_from_outparam__"):
        ret_dids_callback = callbacks.fn_SliceFFIDidListEntry(ret_dids_callback)

    return c_lib.get_dids_by_app_category(app_category_filter_u8, ret_dids_callback)



MODEL_D31L = 1
MODEL_D31F25 = 2
MODEL_D31L24 = 3
MODEL_D21L = 4
MODEL_D31H = 5
MODEL_D31X = 6


TRUE = ctypes.c_uint8(1)
FALSE = ctypes.c_uint8(0)


def _errcheck(returned, success):
    """Checks for FFIErrors and converts them to an exception."""
    if returned == success: return
    else: raise Exception(f"Function returned error: {returned}")


class CallbackVars(object):
    """Helper to be used `lambda x: setattr(cv, "x", x)` when getting values from callbacks."""
    def __str__(self):
        rval = ""
        for var in  filter(lambda x: "__" not in x, dir(self)):
            rval += f"{var}: {getattr(self, var)}"
        return rval


class _Iter(object):
    """Helper for slice iterators."""
    def __init__(self, target):
        self.i = 0
        self.target = target

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i >= self.target.len:
            raise StopIteration()
        rval = self.target[self.i]
        self.i += 1
        return rval


class FFIAppCategory:
    """ Represents the application category for a Data Identifier (DID) in an FFI-safe manner.

 This enum mirrors the categories used in `uds_utils::fdc::AppCategory` that are relevant for FFI exposure."""
    FdA53 = 0
    Bcm = 1
    Vcu = 2
    Evcc = 3
    Ota = 4
    Conn = 5
    Vnd = 6
    Aps = 7
    Tpms = 8
    Dkc = 9
    Zev = 10
    FxnPi = 11
    Thcm = 12
    Scp = 13
    Vmc = 14
    V2l = 15
    FdM7 = 16


class FFIError:
    """ Error codes returned by the FFI functions."""
    #  Operation completed successfully.
    Ok = 0
    #  An invalid argument was provided to the function (e.g., invalid IP format,
    #  out-of-range value, incorrect seed length).
    InvalidArgument = 1
    #  Failed to establish or maintain connection. This can occur during initial
    #  connection or if the background thread terminates unexpectedly.
    ConnectFailed = 2
    #  Received a response from the background thread or DoIP server that was
    #  not expected for the current operation (e.g., getting data when only an
    #  ack was expected).
    UnexpectedResponse = 3
    #  An underlying I/O error occurred (e.g., socket read/write error).
    Io = 4
    #  A numeric conversion error occurred.
    ConvertError = 5
    #  The provided client logical address was invalid.
    InvalidClientLogicalAddr = 6
    #  An unspecified internal error occurred within the library. Check logs for details.
    InternalError = 7
    #  Failed to parse a DoIP message or other data structure.
    ParseError = 8
    #  Received a Diagnostic Message Negative Acknowledge (NACK) from the DoIP server.
    DiagnosticMessageNegativeAck = 9
    #  The DoIP server denied the routing activation request.
    RoutingActivationDenied = 10
    #  The DoIP server responded to routing activation with a different client address
    #  than the one requested.
    RoutingActivationWithDifferentClientAddress = 11
    #  End-of-File reached on the connection, indicating disconnection.
    EOF = 12
    #  The operation timed out waiting for a response.
    Timeout = 13
    #  A null pointer was passed for an argument that requires a valid pointer
    #  (e.g., the output pointer for `doipclient_connect`).
    NullPointerPassed = 14


class FFIDidListEntry(ctypes.Structure):
    """ Represents a single Data Identifier (DID) entry for FFI.

 Contains the DID value (a `u16`) and its `FFIAppCategory`."""

    # These fields represent the underlying C data layout
    _fields_ = [
        ("did", ctypes.c_uint16),
        ("app_category", ctypes.c_int),
    ]

    def __init__(self, did: int = None, app_category: ctypes.c_int = None):
        if did is not None:
            self.did = did
        if app_category is not None:
            self.app_category = app_category

    @property
    def did(self) -> int:
        return ctypes.Structure.__get__(self, "did")

    @did.setter
    def did(self, value: int):
        return ctypes.Structure.__set__(self, "did", value)

    @property
    def app_category(self) -> ctypes.c_int:
        return ctypes.Structure.__get__(self, "app_category")

    @app_category.setter
    def app_category(self, value: ctypes.c_int):
        return ctypes.Structure.__set__(self, "app_category", value)


class Sliceu8(ctypes.Structure):
    # These fields represent the underlying C data layout
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_uint8)),
        ("len", ctypes.c_uint64),
    ]

    def __len__(self):
        return self.len

    def __getitem__(self, i) -> int:
        if i < 0:
            index = self.len+i
        else:
            index = i

        if index >= self.len:
            raise IndexError("Index out of range")

        return self.data[index]

    def copied(self) -> Sliceu8:
        """Returns a shallow, owned copy of the underlying slice.

        The returned object owns the immediate data, but not the targets of any contained
        pointers. In other words, if your struct contains any pointers the returned object
        may only be used as long as these pointers are valid. If the struct did not contain
        any pointers the returned object is valid indefinitely."""
        array = (ctypes.c_uint8 * len(self))()
        ctypes.memmove(array, self.data, len(self) * ctypes.sizeof(ctypes.c_uint8))
        rval = Sliceu8(data=ctypes.cast(array, ctypes.POINTER(ctypes.c_uint8)), len=len(self))
        rval.owned = array  # Store array in returned slice to prevent memory deallocation
        return rval

    def __iter__(self) -> typing.Iterable[ctypes.c_uint8]:
        return _Iter(self)

    def iter(self) -> typing.Iterable[ctypes.c_uint8]:
        """Convenience method returning a value iterator."""
        return iter(self)

    def first(self) -> int:
        """Returns the first element of this slice."""
        return self[0]

    def last(self) -> int:
        """Returns the last element of this slice."""
        return self[len(self)-1]

    def bytearray(self):
        """Returns a bytearray with the content of this slice."""
        rval = bytearray(len(self))
        for i in range(len(self)):
            rval[i] = self[i]
        return rval


class SliceFFIDidListEntry(ctypes.Structure):
    # These fields represent the underlying C data layout
    _fields_ = [
        ("data", ctypes.POINTER(FFIDidListEntry)),
        ("len", ctypes.c_uint64),
    ]

    def __len__(self):
        return self.len

    def __getitem__(self, i) -> FFIDidListEntry:
        if i < 0:
            index = self.len+i
        else:
            index = i

        if index >= self.len:
            raise IndexError("Index out of range")

        return self.data[index]

    def copied(self) -> SliceFFIDidListEntry:
        """Returns a shallow, owned copy of the underlying slice.

        The returned object owns the immediate data, but not the targets of any contained
        pointers. In other words, if your struct contains any pointers the returned object
        may only be used as long as these pointers are valid. If the struct did not contain
        any pointers the returned object is valid indefinitely."""
        array = (FFIDidListEntry * len(self))()
        ctypes.memmove(array, self.data, len(self) * ctypes.sizeof(FFIDidListEntry))
        rval = SliceFFIDidListEntry(data=ctypes.cast(array, ctypes.POINTER(FFIDidListEntry)), len=len(self))
        rval.owned = array  # Store array in returned slice to prevent memory deallocation
        return rval

    def __iter__(self) -> typing.Iterable[FFIDidListEntry]:
        return _Iter(self)

    def iter(self) -> typing.Iterable[FFIDidListEntry]:
        """Convenience method returning a value iterator."""
        return iter(self)

    def first(self) -> FFIDidListEntry:
        """Returns the first element of this slice."""
        return self[0]

    def last(self) -> FFIDidListEntry:
        """Returns the last element of this slice."""
        return self[len(self)-1]




class callbacks:
    """Helpers to define callbacks."""
    fn_SliceFFIDidListEntry = ctypes.CFUNCTYPE(None, SliceFFIDidListEntry)
    fn_Sliceu8 = ctypes.CFUNCTYPE(None, Sliceu8)


