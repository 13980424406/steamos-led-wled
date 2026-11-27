#!/usr/bin/env python3
"""Send a paced Adalight dot pattern to WLED over a Windows COM port."""

import argparse
import time


MAX_ADALIGHT_LEDS = 1 << 16
DEFAULT_BAUD = 115200
DEFAULT_CHUNK_SIZE = 128
DEFAULT_CHUNK_DELAY_MS = 1.0
DEFAULT_REFRESH_INTERVAL = 1.0


def build_adalight_frame(pixels):
    if not pixels or len(pixels) > MAX_ADALIGHT_LEDS:
        raise ValueError(
            f"LED count must be between 1 and {MAX_ADALIGHT_LEDS}"
        )

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
    return b"Ada" + bytes((count_high, count_low, checksum)) + payload


def make_dot_pattern(led_count, spacing):
    if not 1 <= led_count <= MAX_ADALIGHT_LEDS:
        raise ValueError(
            f"LED count must be between 1 and {MAX_ADALIGHT_LEDS}"
        )
    if spacing < 1:
        raise ValueError("spacing must be at least 1")
    return [
        (255, 255, 255) if index % spacing == 0 else (0, 0, 0)
        for index in range(led_count)
    ]


def write_frame(serial_port, frame, chunk_size, chunk_delay, sleep=time.sleep):
    if chunk_size < 1:
        raise ValueError("chunk size must be at least 1")
    if chunk_delay <= 0:
        raise ValueError("chunk delay must be positive")

    for offset in range(0, len(frame), chunk_size):
        chunk = frame[offset:offset + chunk_size]
        written = serial_port.write(chunk)
        if written != len(chunk):
            raise OSError(
                f"short serial write: sent {written} of {len(chunk)} bytes"
            )
        serial_port.flush()
        if offset + len(chunk) < len(frame):
            sleep(chunk_delay)


def open_serial_port(port, baud):
    try:
        import serial
    except ImportError as exc:
        raise RuntimeError(
            "pyserial is required; install it with: py -3 -m pip install pyserial"
        ) from exc

    serial_port = serial.Serial()
    serial_port.port = port
    serial_port.baudrate = baud
    serial_port.timeout = 0.5
    serial_port.write_timeout = 2.0
    serial_port.dtr = False
    serial_port.rts = False
    serial_port.open()
    return serial_port


def send_pattern(serial_port, frame, duration, chunk_size, chunk_delay):
    deadline = time.monotonic() + duration
    while time.monotonic() < deadline:
        write_frame(serial_port, frame, chunk_size, chunk_delay)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return
        time.sleep(min(DEFAULT_REFRESH_INTERVAL, remaining))


def make_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Test WLED Adalight reception by sending a paced pattern of "
            "white dots over a Windows serial port."
        )
    )
    parser.add_argument("port", help="WLED serial port, for example COM4")
    parser.add_argument(
        "--led-count",
        type=int,
        required=True,
        help="LED count configured in WLED",
    )
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--spacing", type=int, default=10)
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument(
        "--chunk-delay-ms", type=float, default=DEFAULT_CHUNK_DELAY_MS
    )
    return parser


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv)
    if not 1 <= args.led_count <= MAX_ADALIGHT_LEDS:
        parser.error(f"--led-count must be between 1 and {MAX_ADALIGHT_LEDS}")
    if args.baud < 1:
        parser.error("--baud must be positive")
    if args.duration <= 0:
        parser.error("--duration must be positive")
    if args.chunk_size < 1:
        parser.error("--chunk-size must be positive")
    if args.chunk_delay_ms <= 0:
        parser.error("--chunk-delay-ms must be positive")
    if args.spacing < 1:
        parser.error("--spacing must be positive")

    pixels = make_dot_pattern(args.led_count, args.spacing)
    frame = build_adalight_frame(pixels)
    black_frame = build_adalight_frame([(0, 0, 0)] * args.led_count)
    chunk_delay = args.chunk_delay_ms / 1000.0
    try:
        serial_port = open_serial_port(args.port, args.baud)
    except (OSError, RuntimeError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    lit_leds = list(range(0, args.led_count, args.spacing))
    print(
        f"Opened {args.port} at {args.baud} baud; "
        f"{len(lit_leds)} white dots across {args.led_count} LEDs."
    )
    print(
        f"Sending {len(frame)}-byte Adalight frames in "
        f"{args.chunk_size}-byte chunks for {args.duration:g} seconds."
    )

    try:
        send_pattern(
            serial_port,
            frame,
            args.duration,
            args.chunk_size,
            chunk_delay,
        )
    except KeyboardInterrupt:
        print("\nInterrupted; sending a black frame.")
    finally:
        try:
            write_frame(
                serial_port,
                black_frame,
                args.chunk_size,
                chunk_delay,
            )
            print("Black frame sent.")
        finally:
            serial_port.close()


if __name__ == "__main__":
    main()
