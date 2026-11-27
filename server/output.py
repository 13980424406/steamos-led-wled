"""Output routing."""

import sys
import time


class FanoutOutput:
    """Send each frame to every configured output, reporting failures per target."""

    def __init__(self, outputs, error_interval=5.0):
        if not outputs:
            raise ValueError("at least one LED output must be configured")
        self.outputs = tuple(outputs)
        self.error_interval = error_interval
        self._last_errors = {}

    def send_pixels(self, pixels):
        now = time.monotonic()
        for name, output in self.outputs:
            try:
                output.send_pixels(pixels)
                self._last_errors.pop(name, None)
            except Exception as exc:
                previous = self._last_errors.get(name)
                if previous is None or previous[0] != str(exc) or \
                        now - previous[1] >= self.error_interval:
                    print(f"{name} LED output error: {exc}", file=sys.stderr)
                    self._last_errors[name] = (str(exc), now)

    def close(self):
        for name, output in self.outputs:
            try:
                output.close()
            except Exception as exc:
                print(f"{name} LED output close error: {exc}", file=sys.stderr)
