import datetime
import dataclasses
import enum

from udsoncan import DidCodec

class PpStatus(enum.IntEnum):
    Unplug = 0
    Plugin = 1
    S3Pressed = 2

class ElecLockStatus(enum.IntEnum):
    Unlock = 0
    Lock = 1

class BmsChoiceChargeMode(enum.IntEnum):
    NoChargeMode = 0
    Dc = 1
    Ac = 2
    Bc = 3
    DcPnc = 4
    AcPnc = 5

@dataclasses.dataclass
class EvccDebugMessage:
    second: int
    minute: int
    hour: int
    day: int
    month: int
    gbdc_debug_code: int
    slac_debug_code: int
    evcc_pwr_up_state_debug_code: int
    v2g_dc_debug_code: int
    v2g_ac_debug_code: int
    plc_charge_end: int
    ev_charge_end: int
    charge_fail_code: int
    pp_status: PpStatus
    elec_lock_status: ElecLockStatus
    bms_choice_charge_mode: BmsChoiceChargeMode

    @staticmethod
    def codec() -> DidCodec:
        return EvccDebugMessageCodec()

    def __str__(self) -> str:
        instant = f"{self.month}/{self.day} {self.hour}:{self.minute}:{self.second}"
        return f"""
EvccDebugCode as of {instant}:
    gbdc_debug_code: {hex(self.gbdc_debug_code)}
    slac_debug_code: {hex(self.slac_debug_code)}
    evcc_pwr_up_state_debug_code: {hex(self.evcc_pwr_up_state_debug_code)}
    v2g_dc_debug_code: {hex(self.v2g_dc_debug_code)}
    v2g_ac_debug_code: {hex(self.v2g_ac_debug_code)}
    plc_charge_end: {hex(self.plc_charge_end)}
    ev_charge_end: {hex(self.ev_charge_end)}
    charge_fail_code: {hex(self.charge_fail_code)}
    pp_status: {self.pp_status.name}
    elec_lock_status: {self.elec_lock_status.name}
    bms_choice_charge_mode: {self.bms_choice_charge_mode.name}
    """

class EvccDebugMessageCodec(DidCodec):
    EXPECTED_PAYLOAD_LEN = 16
    # Only `decode` is defined because this DID is read only.
    def decode(self, raw_bytes: bytes) -> EvccDebugMessage:
        assert len(raw_bytes) == self.EXPECTED_PAYLOAD_LEN
        # Each of the last three bytes has a valid Enum representation.
        # Others can be treated as an u8.
        pp_status = PpStatus(raw_bytes[13])
        elec_lock_status = ElecLockStatus(raw_bytes[14])
        bms_choice_charge_mode = BmsChoiceChargeMode(raw_bytes[15])
        return EvccDebugMessage(*raw_bytes[:13], pp_status, elec_lock_status, bms_choice_charge_mode)

    def __len__(self) -> int:
        return self.EXPECTED_PAYLOAD_LEN
