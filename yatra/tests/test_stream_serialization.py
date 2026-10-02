import unittest

from app.model import WeatherResponseModel
from app.routes import stream as stream_module


class StreamSerializationTests(unittest.TestCase):
    def test_format_sse_serializes_pydantic_models(self):
        weather = WeatherResponseModel(
            date="2026-06-30",
            condition="Sunny",
            temperature_high=32.0,
            temperature_low=24.0,
            humidity=50.0,
            rain_chance=10.0,
        )

        payload = stream_module.format_sse({"weather_data": [weather]})

        self.assertIn('"weather_data"', payload)
        self.assertIn('"date": "2026-06-30"', payload)
        self.assertIn('"condition": "Sunny"', payload)


if __name__ == "__main__":
    unittest.main()
