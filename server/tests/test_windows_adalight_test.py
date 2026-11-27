import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from wled_usb_cdc_adalight_test import (
    build_adalight_frame,
    make_dot_pattern,
    open_serial_port,
    write_frame,
)


class AdalightTestProgramTests(unittest.TestCase):
    def test_builds_wled_frame_for_320_leds(self):
        frame = build_adalight_frame([(255, 255, 255)] * 320)

        self.assertEqual(frame[:6], b"Ada\x01\x3f\x6b")
        self.assertEqual(len(frame), 6 + 320 * 3)

    def test_dot_pattern_turns_on_each_spaced_led(self):
        pixels = make_dot_pattern(21, 10)

        self.assertEqual(
            [index for index, pixel in enumerate(pixels) if pixel == (255, 255, 255)],
            [0, 10, 20],
        )
        self.assertEqual(pixels[1], (0, 0, 0))

    def test_frame_is_written_in_paced_chunks(self):
        class FakeSerialPort:
            def __init__(self):
                self.chunks = []
                self.flush_count = 0

            def write(self, data):
                self.chunks.append(bytes(data))
                return len(data)

            def flush(self):
                self.flush_count += 1

        serial_port = FakeSerialPort()
        delays = []
        write_frame(
            serial_port,
            bytes(range(256)) + b"!" * 44,
            chunk_size=128,
            chunk_delay=0.001,
            sleep=delays.append,
        )

        self.assertEqual([len(chunk) for chunk in serial_port.chunks], [128, 128, 44])
        self.assertEqual(serial_port.flush_count, 3)
        self.assertEqual(delays, [0.001, 0.001])

    def test_dtr_and_rts_are_disabled_before_open(self):
        events = []

        class FakeSerialPort:
            def __setattr__(self, name, value):
                object.__setattr__(self, name, value)
                if name in ("dtr", "rts"):
                    events.append((name, value))

            def open(self):
                events.append(("open",))

        with patch.dict(
            sys.modules,
            {"serial": types.SimpleNamespace(Serial=FakeSerialPort)},
        ):
            open_serial_port("COM4", 921600)

        self.assertEqual(events, [("dtr", False), ("rts", False), ("open",)])


if __name__ == "__main__":
    unittest.main()
