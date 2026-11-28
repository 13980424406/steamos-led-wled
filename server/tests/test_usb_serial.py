from contextlib import redirect_stderr
import io
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from led_server import load_config
from output import FanoutOutput
from usb_serial import (
    ADALIGHT_HEADER,
    UsbSerialSender,
    encode_adalight_frame,
    encode_json_serial_frame,
)


class AdalightEncodingTests(unittest.TestCase):
    def test_frame_contains_header_count_checksum_and_rgb_payload(self):
        frame = encode_adalight_frame([(1, 2, 3), (250, 0, 255)])

        self.assertEqual(frame[:3], ADALIGHT_HEADER)
        self.assertEqual(frame[3:5], b"\x00\x01")
        self.assertEqual(frame[5], frame[3] ^ frame[4] ^ 0x55)
        self.assertEqual(frame[6:], bytes((1, 2, 3, 250, 0, 255)))

    def test_rejects_bad_pixel_count_and_channels(self):
        for pixels in ([], [(1, 2, 3)] * 257, [(1, 2)], [(0, 0, 256)]):
            with self.subTest(pixels=len(pixels)):
                with self.assertRaises(ValueError):
                    encode_adalight_frame(pixels)

    def test_encodes_maximum_supported_pixel_count(self):
        frame = encode_adalight_frame([(0, 0, 0)] * 256)

        self.assertEqual(frame[3:5], b"\x00\xff")
        self.assertEqual(len(frame), 6 + 256 * 3)


class JsonSerialEncodingTests(unittest.TestCase):
    def test_frame_is_newline_delimited_wled_json_with_hex_pixels(self):
        frame = encode_json_serial_frame([(1, 2, 3), (250, 0, 255)])

        self.assertEqual(
            frame,
            b'{"seg":{"i":["010203","FA00FF"]}}\n',
        )

    def test_rejects_bad_pixel_count_and_channels(self):
        for pixels in ([], [(1, 2, 3)] * 257, [(1, 2)], [(0, 0, 256)]):
            with self.subTest(pixels=len(pixels)):
                with self.assertRaises(ValueError):
                    encode_json_serial_frame(pixels)

    def test_sender_turns_wled_on_once_before_setting_pixels(self):
        sender = UsbSerialSender.__new__(UsbSerialSender)
        sender.protocol = "json"
        sender.device = "/dev/fake"
        sender.write_timeout = 1.0
        sender._write_lock = threading.Lock()
        sender._json_initialized = False
        sender.fd = 7
        writes = []

        def capture_write(_fd, payload):
            data = bytes(payload)
            writes.append(data)
            return len(data)

        with patch("usb_serial.select.select", return_value=([], [7], [])), \
                patch("usb_serial.os.write", side_effect=capture_write):
            sender.send_pixels([(1, 2, 3)])
            sender.send_pixels([(4, 5, 6)])

        self.assertEqual(
            b"".join(writes),
            b'{"on":true}\n'
            b'{"seg":{"i":["010203"]}}\n'
            b'{"seg":{"i":["040506"]}}\n',
        )


class OutputTests(unittest.TestCase):
    def test_fanout_continues_after_one_output_fails(self):
        class Output:
            def __init__(self, fail=False):
                self.fail = fail
                self.calls = 0

            def send_pixels(self, pixels):
                self.calls += 1
                if self.fail:
                    raise OSError("disconnected")

            def close(self):
                pass

        first = Output(fail=True)
        second = Output()
        fanout = FanoutOutput([("failed", first), ("healthy", second)])
        errors = io.StringIO()
        with redirect_stderr(errors):
            fanout.send_pixels([(0, 0, 0)])

        self.assertEqual(first.calls, 1)
        self.assertEqual(second.calls, 1)
        self.assertIn("failed LED output error", errors.getvalue())


class ConfigurationTests(unittest.TestCase):
    def read_config(self, content):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.ini"
            path.write_text("[steamos-led-wled]\n" + content, encoding="utf-8")
            return load_config(str(path))

    def test_existing_config_defaults_to_wled_mode(self):
        config = self.read_config("wled_host = 192.0.2.1\n")

        self.assertEqual(config["output_mode"], "wled")
        self.assertEqual(config["num_leds"], 8)
        self.assertEqual(config["usb_serial_protocol"], "adalight")

    def test_config_accepts_maximum_output_led_count(self):
        config = self.read_config("num_leds = 256\n")

        self.assertEqual(config["num_leds"], 256)

    def test_config_rejects_output_led_count_above_maximum(self):
        with self.assertRaisesRegex(ValueError, "between 1 and 256"):
            self.read_config("num_leds = 257\n")

    def test_installer_template_loads_after_placeholder_substitution(self):
        project_dir = Path(__file__).resolve().parents[2]
        content = (project_dir / "server" / "steamos-led-wled.conf").read_text(
            encoding="utf-8"
        )
        replacements = {
            "__WLED_HOST__": "192.0.2.1",
            "__WLED_PORT__": "21324",
            "__NUM_LEDS__": "17",
            "__OUTPUT_MODE__": "both",
            "__USB_SERIAL_DEVICE__": "/dev/ttyACM0",
            "__USB_SERIAL_PROTOCOL__": "json",
            "__TEMP_OVERLAY__": "true",
            "__NOTIFY_OVERLAY__": "true",
            "__AUDIO_OVERLAY__": "true",
        }
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        config = self.read_config(content.partition("]\n")[2])

        self.assertEqual(config["output_mode"], "both")
        self.assertEqual(config["usb_serial_protocol"], "json")

    def test_config_rejects_unknown_usb_serial_protocol(self):
        with self.assertRaisesRegex(ValueError, "usb_serial_protocol"):
            self.read_config("usb_serial_protocol = unknown\n")

    def test_usb_mode_ignores_legacy_matrix_layout_settings(self):
        config = self.read_config(
            "output_mode = usb\n"
            "num_leds = 17\n"
            "wled_host =\n"
            "usb_serial_device = /dev/ttyACM0\n"
            "matrix_width = 8\n"
            "matrix_height = 8\n"
            "matrix_map = [0, 1]\n"
        )

        self.assertEqual(config["output_mode"], "usb")
        self.assertNotIn("matrix_map", config)


if __name__ == "__main__":
    unittest.main()
