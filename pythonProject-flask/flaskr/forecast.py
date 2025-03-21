from flask import Flask, request, jsonify
from openai import OpenAI
from markupsafe import escape
import requests

app = Flask(__name__)


@app.route("/forecast/<latitude>/<longitude>", methods=['GET'])
def get_forecast(latitude, longitude):
    forecast_url = f"https://api.weather.gov/points/{escape(latitude)},{escape(longitude)}"

    forecast_response = requests.get(forecast_url)

    if forecast_response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve forecast data.'}), forecast_response.status_code

    forecast_data = forecast_response.json()
    daily_report_url = forecast_data["properties"]["forecast"]

    return get_detailed_forecast(daily_report_url)


def get_detailed_forecast(detailed_forecast_url):
    detailed_forecast = []
    detailed_forecast_response = requests.get(detailed_forecast_url)

    if detailed_forecast_response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve detailed forecast data.'}), detailed_forecast_response.status_code

    detailed_forecast_json = detailed_forecast_response.json()

    detailed_forecast_periods = detailed_forecast_json["properties"]["periods"]

    for period in detailed_forecast_periods:
        detailed_forecast.append(f"{period['name']} is going to be {period['detailedForecast']}")

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Summarize this content " + str(detailed_forecast)
            }
        ]
    )

    return completion.choices[0].message.content


if __name__ == '__main__':
    app.run(debug=True, port=5001)
