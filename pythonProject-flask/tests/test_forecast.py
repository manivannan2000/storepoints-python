import unittest
from unittest.mock import patch, MagicMock
from flaskr.forecast import app
from flask import jsonify

class TestForecastApp(unittest.TestCase):
    def setUp(self):
        # Sets up the Flask test client
        self.app = app.test_client()
        self.app.testing = True

    @patch("flaskr.forecast.requests.get")
    @patch("flaskr.forecast.OpenAI")
    def test_get_forecast_success(self, mock_openai, mock_requests_get):
        # 1. Mock the first requests call (points lookup)
        mock_points_response = MagicMock()
        mock_points_response.status_code = 200
        mock_points_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/ABC/123/forecast"
            }
        }

        # 2. Mock the second requests call (detailed forecast data)
        mock_forecast_response = MagicMock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.json.return_value = {
            "properties": {
                "periods": [
                    {
                        "name": "Tonight",
                        "detailedForecast": "Clear with a low around 65."
                    },
                    {
                        "name": "Tomorrow",
                        "detailedForecast": "Sunny with a high near 85."
                    }
                ]
            }
        }

        # Sequence of responses
        mock_requests_get.side_effect = [mock_points_response, mock_forecast_response]

        # 3. Mock the OpenAI client
        mock_openai_instance = mock_openai.return_value
        mock_openai_instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Mocked summary response"))]
        )

        # 4. Call the endpoint
        response = self.app.get("/forecast/35.000/-110.000")

        # 5. Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Mocked summary response", response.data.decode())

        mock_requests_get.assert_any_call("https://api.weather.gov/points/35.000,-110.000")
        mock_requests_get.assert_any_call("https://api.weather.gov/gridpoints/ABC/123/forecast")

        mock_openai_instance.chat.completions.create.assert_called_once()

    @patch("flaskr.forecast.requests.get")
    def test_get_forecast_points_api_failure(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        response = self.app.get("/forecast/35.000/-110.000")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Failed to retrieve forecast data.", response.data.decode())

    @patch("flaskr.forecast.requests.get")
    def test_get_detailed_forecast_api_failure(self, mock_requests_get):
        # The points API call succeeds
        mock_points_response = MagicMock()
        mock_points_response.status_code = 200
        mock_points_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/ABC/123/forecast"
            }
        }

        # The second call fails
        mock_forecast_response = MagicMock()
        mock_forecast_response.status_code = 500

        mock_requests_get.side_effect = [mock_points_response, mock_forecast_response]

        response = self.app.get("/forecast/35.000/-110.000")
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to retrieve detailed forecast data.", response.data.decode())

if __name__ == "__main__":
    unittest.main()
