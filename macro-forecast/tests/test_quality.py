import unittest

from macro_forecast.quality import confidence_tag


class QualityTest(unittest.TestCase):
    def test_confidence_tag(self):
        self.assertEqual(confidence_tag(0.7), "HIGH")
        self.assertEqual(confidence_tag(0.3), "MED")
        self.assertEqual(confidence_tag(0.1), "LOW")


if __name__ == "__main__":
    unittest.main()
