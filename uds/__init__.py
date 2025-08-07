import os
from uds import ffi

package_directory = os.path.dirname(os.path.abspath(__file__))
ffi.init_lib(os.path.join(package_directory, "libuds_client.so"))
ffi.doipclient_init()
