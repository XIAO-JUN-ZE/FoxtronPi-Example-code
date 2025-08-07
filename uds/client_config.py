import os
from typing import Optional, Dict, Any  # Added Dict, Any for type hints
from uds.client import (
    decrypt_seed_with_model,
    MODEL_D31L,
    MODEL_D31F25,
    MODEL_D31L24,
    MODEL_D21L,
    MODEL_D31H,
    MODEL_D31X,
)
from uds.evcc_debug_code import EvccDebugMessageCodec
import udsoncan  # Required for DidCodec
from udsoncan.configs import default_client_config


class RawBytesCodec(udsoncan.DidCodec):
    """
    A simple codec that reads all remaining bytes for a DID
    and returns them as is.
    Used as a default for DIDs not explicitly defined in the configuration.
    """

    def encode(self, *did_value: Any) -> bytes:
        raise NotImplementedError("RawBytesCodec is for decoding only.")

    def decode(self, did_payload: bytes) -> bytes:
        return did_payload  # Return raw bytes

    def __len__(self) -> int:
        # Instruct udsoncan to read all remaining data for this DID
        raise udsoncan.DidCodec.ReadAllRemainingData


MODEL_DEFAULT = MODEL_D31L24

# Mapping from integer (for user input) to model constant
INT_TO_MODEL_MAP: Dict[int, int] = {
    1: MODEL_D31L,
    2: MODEL_D31F25,
    3: MODEL_D31L24,
    4: MODEL_D21L,
    5: MODEL_D31H,
    6: MODEL_D31X,
}

# Mapping from the short string name (for env var) to model constant
# Keys are expected like "D31L", "D31F25", etc. (case-insensitive)
SHORT_NAME_TO_MODEL_MAP: Dict[str, int] = {
    "D31L": MODEL_D31L,
    "D31F25": MODEL_D31F25,
    "D31L24": MODEL_D31L24,
    "D21L": MODEL_D21L,
    "D31H": MODEL_D31H,
    "D31X": MODEL_D31X,
}

# Mapping from model constant back to its short name (for display)
MODEL_TO_SHORT_NAME_MAP: Dict[int, str] = {
    v: k for k, v in SHORT_NAME_TO_MODEL_MAP.items()
}


def client_config(model: Optional[int] = 6) -> Dict[str, Any]:
    """
    Configures the UDS client with the specified car model.

    The model is determined in the following order:
    1. The `model` argument passed to the function (expects model constant, e.g., MODEL_D31L).
    2. The `CAR_MODEL` environment variable (expects short string name, e.g., "D31L").
    3. User input prompt (expects integer 1-5).

    :param model: The car model constant (e.g., MODEL_D31L).
                  If None, the function will try the environment variable or prompt the user.
    :return: A dictionary containing the client configuration.
    :raises ValueError: If the provided model argument is invalid.
    :raises RuntimeError: If the model cannot be determined.
    """
    determined_model: Optional[int] = (
        model  # Use a separate variable to store the result
    )

    if determined_model is not None:
        # Validate the provided model argument (ensure it's one of the known constants)
        if (
            determined_model not in MODEL_TO_SHORT_NAME_MAP
        ):  # Check if the constant is known
            raise ValueError(f"Invalid model argument provided: {determined_model}")
        print(
            f"Using car model {MODEL_TO_SHORT_NAME_MAP.get(determined_model, 'UNKNOWN')} provided as argument."
        )
    else:
        # Try getting model from environment variable (short string name)
        env_model_str = os.environ.get("CAR_MODEL")
        if env_model_str:
            # Normalize the string (remove whitespace, convert to upper case for robust matching)
            normalized_env_model_str = env_model_str.strip().upper()
            if normalized_env_model_str in SHORT_NAME_TO_MODEL_MAP:
                determined_model = SHORT_NAME_TO_MODEL_MAP[normalized_env_model_str]
                print(
                    f"Using car model '{env_model_str}' from CAR_MODEL environment variable."
                )
            else:
                print(
                    f"Warning: Invalid value '{env_model_str}' in CAR_MODEL environment variable. "
                    f"Expected one of {list(SHORT_NAME_TO_MODEL_MAP.keys())}. Falling back to user input."
                )

        # If model is still None, prompt user (integer input)
        while determined_model is None:
            try:
                # Build the prompt string dynamically using short names
                prompt_options_display = ", ".join(
                    [
                        f"{k} for {MODEL_TO_SHORT_NAME_MAP[v]}"
                        for k, v in INT_TO_MODEL_MAP.items()
                    ]
                )
                value_str = input(f"Enter car model: {prompt_options_display} ")
                value = int(value_str)
                if value in INT_TO_MODEL_MAP:
                    determined_model = INT_TO_MODEL_MAP[value]
                    print(
                        f"Using car model {MODEL_TO_SHORT_NAME_MAP.get(determined_model, 'UNKNOWN')} from user input."
                    )
                    # Loop condition `determined_model is None` handles exit
                else:
                    print(
                        f"Invalid input. Please enter a valid car model number ({list(INT_TO_MODEL_MAP.keys())})."
                    )
            except ValueError:
                print(f"Invalid input '{value_str}'. Please enter a number.")
            except EOFError:  # Handle case where input stream is closed (e.g., piping)
                print("\nInput stream closed. Cannot prompt for model.")
                break  # Exit the loop

    # Ensure model is set before proceeding
    if determined_model is None:
        # This might happen if EOFError occurred in the prompt loop
        raise RuntimeError(
            "Failed to determine car model. No argument, valid environment variable, or user input provided."
        )

    config = default_client_config.copy()
    config["security_algo"] = decrypt_seed_with_model(determined_model)

    # Data Identifiers (rest remains the same)
    config["data_identifiers"] = {
        0x0201: "1s",  # XWD
        0x0202: "8s",  # DKC
        0x0203: "1s",  # Dyno mode
        0x0206: "3s",
        0x0207: "3s",
        0x0301: "1s",
        0x0302: "1s",
        0x0303: "1s",
        0x0304: "1s",
        0x0305: "1s",
        0x0306: "1s",
        0x0307: "1s",
        0x0501: "1s",  # EVCC supported protocol
        0x0504: "6s",  # EVCC MAC address
        0x050D: EvccDebugMessageCodec,
        0x0610: "1s",
        0x0611: "1s",
        0x07F1: "496s",  # Smart Factory Write Data to CONN
        0x0B01: "4s",
        0x0B05: "4s",
        0x0E04: "16s",  # FD system time YYYYmmddTHHMMSSZ,  16 bytes
        0x0F05: "90s",
        0xF090: "22s",  # FVT VIN
        0xF16F: "10s",  # CAN message map vesrion
        0xF181: "10s",  # Partition number
        0xF184: "10s",
        0xF187: "10s",  # Spare part number
        0xF190: "17s",  # VIN code
        0xF193: "10s",  # HW version
        0xF195: "10s",  # SW version
        0xF199: "10s",
        0xF400: "4s",  # J1979DA Annex A
        0xF41C: "B",
        0xF41F: "H",
        0xF420: "4s",  # J1979DA Annex A
        0xF421: "H",
        0xF430: "B",
        0xF440: "4s",  # J1979DA Annex A
        0xF460: "4s",  # J1979DA Annex A
        0xF480: "4s",  # J1979DA Annex A
        0xF4A0: "4s",  # J1979DA Annex A
        0xF4C0: "4s",  # J1979DA Annex A
        0xF4E0: "4s",  # J1979DA Annex A
        0xF800: "4s",  # J1979DA Annex A
        0xF810: "B",  # Protocol detection (1 byte unsigned char)
        0xF820: "4s",  # J1979DA Annex A
        0xF840: "4s",  # J1979DA Annex A
        0xF860: "4s",  # J1979DA Annex A
        0xF880: "4s",  # J1979DA Annex A
        0xF8A0: "4s",  # J1979DA Annex A
        0xF8C0: "4s",  # J1979DA Annex A
        0xF8E0: "4s",  # J1979DA Annex A
        #FoxPi
        0x1001: "21s", # FoxPi_Driving_Ctrl
        0x1002: "13s", # FoxPi_Motion_Status
        0x1003: "13s", # FoxPi_Brake_Status
        0x1004: "16s", # FoxPi_WheelSpeed
        0x1005: "11s", # FoxPi_EPS_Status
        0x1006: "2s", # FoxPi_Button_Status
        0x1007: "20s", # FoxPi_USS_Distance
        0x1008: "2s", # FoxPi_USS_Fault_Status
        0x1009: "1s", # FoxPi_PTG_USS_SW
        0x100A: "2s", # FoxPi_Switch_Status
        0x100B: "2s", # FoxPi_Lamp_Status
        0x100C: "6s", # FoxPi_Lamp_Ctrl
        0x100D: "4s", # FoxPi_Battery_Status
        0x100E: "13s", # FoxPi_TPMS_Status
        0x100F: "3s", # FoxPi_Pedal_position
        0x1010: "11s", # FoxPi_Motor_Status
        0x1011: "3s", # FoxPi_Shifter_allow
        0x1012: "1s", # FoxPi_Ctrl_Enable_Switch
    }

    # Add a default codec for unknown DIDs to treat them as raw bytes.
    # This prevents ConfigError for DIDs not explicitly defined when reading.
    if "default" not in config["data_identifiers"]:
        config["data_identifiers"]["default"] = RawBytesCodec()

    return config
