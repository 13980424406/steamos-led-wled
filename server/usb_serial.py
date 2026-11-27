"""USB serial transport for the SteamOS LED RGB frame protocol."""

import errno
import os
import select
import sys
import threading
import time


ADALIGHT_HEADER = b"Ada"
MAX_PIXELS = 256


def encode_adalight_frame(pixels):
    """Encode RGB pixels as a WLED-compatible Adalight serial frame."""
    if not pixels or len(pixels) > MAX_PIXELS:
        raise ValueError(f"pixel count must be between 1 and {MAX_PIXELS}")

    payload = bytearray()
    for pixel in pixels:
        if len(pixel) != 3:
            raise ValueError("each pixel must contain exactly three channels")
        for channel in pixel:
            if not isinstance(channel, int) or not 0 <= channel <= 255:
                raise ValueError("RGB channels must be integers between 0 and 255")
            payload.append(channel)

    encoded_count = len(pixels) - 1
    count_high = (encoded_count >> 8) & 0xFF
    count_low = encoded_count & 0xFF
    checksum = count_high ^ count_low ^ 0x55
    return ADALIGHT_HEADER + bytes((count_high, count_low, checksum)) + payload


class UsbSerialSender:
    """Write RGB frames to a Linux USB serial device without third-party packages."""

    _BAUD_RATES = {
        9600: "B9600",
        19200: "B19200",
        38400: "B38400",
        57600: "B57600",
        115200: "B115200",
        230400: "B230400",
        460800: "B460800",
        921600: "B921600",
    }

    def __init__(self, device, baud=115200, write_timeout=1.0):
        if baud not in self._BAUD_RATES:
            raise ValueError(f"unsupported serial baud rate: {baud}")
        try:
            import termios
            import tty
        except ImportError as exc:
            raise RuntimeError("USB serial output requires a POSIX/Linux host") from exc

        self.device = device
        self.write_timeout = write_timeout
        self._write_lock = threading.Lock()
        self.fd = os.open(device, os.O_WRONLY | os.O_NOCTTY)
        try:
            tty.setraw(self.fd)
            settings = termios.tcgetattr(self.fd)
            speed = getattr(termios, self._BAUD_RATES[baud], None)
            if speed is None:
                raise ValueError(f"baud rate {baud} is unavailable on this system")
            settings[2] |= termios.CLOCAL | termios.CREAD
            settings[4] = speed
            settings[5] = speed
            termios.tcsetattr(self.fd, termios.TCSANOW, settings)
        except Exception:
            os.close(self.fd)
            self.fd = None
            raise

    def send_pixels(self, pixels):
        frame = encode_adalight_frame(pixels)
        with self._write_lock:
            remaining = memoryview(frame)
            deadline = time.monotonic() + self.write_timeout
            while remaining:
                timeout = deadline - time.monotonic()
                if timeout <= 0:
                    raise TimeoutError(f"timed out writing to {self.device}")
                try:
                    _, writable, _ = select.select([], [self.fd], [], timeout)
                    if not writable:
                        raise TimeoutError(f"timed out writing to {self.device}")
                    written = os.write(self.fd, remaining)
                    if written == 0:
                        raise OSError(errno.EIO, "serial device accepted no data")
                    remaining = remaining[written:]
                except InterruptedError:
                    continue

    def close(self):
        with self._write_lock:
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
