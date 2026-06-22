from pathlib import Path
import sys
import unittest

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from helpers.transition_freeze_detector import compute_frame_stats, quantize_duration_ms


class TransitionFreezeDetectorTests(unittest.TestCase):
    def test_quantize_duration_to_30fps_grid(self):
        result = quantize_duration_ms(101)
        self.assertEqual(result["target_frames"], 3)
        self.assertAlmostEqual(result["quantized_duration_ms"], 100.0)
        self.assertLessEqual(abs(result["duration_quantization_error_ms"]), 16.7)

    def test_exact_duplicate_tail_run(self):
        temp = Path(__file__).parent / "_tmp_transition_frames"
        temp.mkdir(exist_ok=True)
        try:
            frames = []
            for index, value in enumerate([0, 40, 80, 80, 80], start=1):
                path = temp / f"frame_{index}.png"
                Image.fromarray(np.full((8, 8), value, dtype=np.uint8)).save(path)
                frames.append(path)
            stats = compute_frame_stats(frames)
            self.assertEqual(stats.exact_duplicate_tail_frames, 3)
            self.assertGreaterEqual(stats.exact_duplicate_tail_ms, 60)
        finally:
            for path in temp.glob("*"):
                path.unlink()
            temp.rmdir()


if __name__ == "__main__":
    unittest.main()
