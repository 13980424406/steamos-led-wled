import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from led_server import (
    PIXEL_SIZE,
    PIXELS_OFFSET,
    SNAPSHOT_SIZE,
    SRC_NUM_LEDS,
    blend_frames,
    extract_pixels,
    remap_snapshot,
)


def make_snapshot(red_values=None):
    if red_values is None:
        red_values = list(range(SRC_NUM_LEDS))
    snapshot = bytearray(SNAPSHOT_SIZE)
    snapshot[26] = 255
    for i, red in enumerate(red_values):
        offset = PIXELS_OFFSET + i * PIXEL_SIZE
        snapshot[offset:offset + PIXEL_SIZE] = bytes((red, 0, 0, 255))
    return bytes(snapshot)


class LedRemappingTests(unittest.TestCase):
    def test_seventeen_outputs_preserve_source_snapshot(self):
        snapshot = make_snapshot()

        self.assertEqual(remap_snapshot(snapshot, SRC_NUM_LEDS), snapshot)

    def test_downsampling_averages_source_leds_and_keeps_snapshot_size(self):
        remapped = remap_snapshot(make_snapshot(), 1)

        self.assertEqual(len(remapped), SNAPSHOT_SIZE)
        self.assertEqual(remapped[PIXELS_OFFSET], 8)
        self.assertEqual(remapped[PIXELS_OFFSET + PIXEL_SIZE:], bytes(16 * PIXEL_SIZE))

    def test_double_resolution_distributes_each_source_led_twice(self):
        snapshot = make_snapshot()
        remapped = remap_snapshot(snapshot, 34)

        self.assertEqual(len(remapped), PIXELS_OFFSET + 34 * PIXEL_SIZE)
        for output_index in range(34):
            source_offset = PIXELS_OFFSET + (output_index // 2) * PIXEL_SIZE
            output_offset = PIXELS_OFFSET + output_index * PIXEL_SIZE
            self.assertEqual(
                remapped[output_offset:output_offset + PIXEL_SIZE],
                snapshot[source_offset:source_offset + PIXEL_SIZE],
            )
        self.assertEqual(len(extract_pixels(remapped, 34)), 34)

    def test_upsampling_averages_overlapping_source_boundaries(self):
        values = [0, 100] + [0] * (SRC_NUM_LEDS - 2)
        remapped = remap_snapshot(make_snapshot(values), 20)
        output_offset = PIXELS_OFFSET + PIXEL_SIZE

        self.assertEqual(remapped[output_offset], 82)

    def test_maximum_frame_can_be_extracted_and_blended(self):
        remapped = remap_snapshot(make_snapshot(), 256)

        self.assertEqual(len(remapped), PIXELS_OFFSET + 256 * PIXEL_SIZE)
        self.assertEqual(len(extract_pixels(remapped, 256)), 256)
        self.assertEqual(len(blend_frames(remapped, remapped, 0.5, 256)), len(remapped))


if __name__ == "__main__":
    unittest.main()
