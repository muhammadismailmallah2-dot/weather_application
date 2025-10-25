import requests
import json
from datetime import datetime
from colorama import Fore, Style, init

print("This project is developed by Muhammad Ismail")
# Initialize colorama for colored terminal output
init(autoreset=True)


class WeatherApp:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url_current = "https://api.openweathermap.org/data/2.5/weather"
        self.base_url_forecast = "https://api.openweathermap.org/data/2.5/forecast"

    def get_current_weather(self, city):
        """Fetch current weather"""
        url = f"{self.base_url_current}?q={city}&appid={self.api_key}&units=metric"
        res = requests.get(url)
        return res.json() if res.status_code == 200 else None

    def get_forecast(self, city):
        """Fetch 5-day weather forecast"""
        url = f"{self.base_url_forecast}?q={city}&appid={self.api_key}&units=metric"
        res = requests.get(url)
        return res.json() if res.status_code == 200 else None

    def parse_current(self, data):
        """Extract current weather info"""
        return {
            "City": data["name"],
            "Temperature (°C)": data["main"]["temp"],
            "Weather": data["weather"][0]["description"].title(),
            "Humidity (%)": data["main"]["humidity"],
            "Wind Speed (m/s)": data["wind"]["speed"],
            "Date & Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def parse_forecast(self, data):
        """Summarize 5-day forecast (one reading per day)"""
        daily_data = {}
        for entry in data["list"]:
            date_str = entry["dt_txt"].split(" ")[0]
            temp = entry["main"]["temp"]
            desc = entry["weather"][0]["description"].title()
            if date_str not in daily_data:
                daily_data[date_str] = {"temps": [], "descriptions": []}
            daily_data[date_str]["temps"].append(temp)
            daily_data[date_str]["descriptions"].append(desc)

        forecast_summary = []
        for date_str, values in daily_data.items():
            avg_temp = sum(values["temps"]) / len(values["temps"])
            common_weather = max(set(values["descriptions"]), key=values["descriptions"].count)
            forecast_summary.append({
                "Date": date_str,
                "Avg Temp (°C)": round(avg_temp, 1),
                "Main Weather": common_weather
            })
        return forecast_summary

    def save_to_file(self, data, filename="weather_log.json"):
        """Save results to JSON file"""
        try:
            with open(filename, "r") as f:
                file_data = json.load(f)
        except FileNotFoundError:
            file_data = []
        file_data.append(data)
        with open(filename, "w") as f:
            json.dump(file_data, f, indent=4)

    def display_weather(self, info, forecast):
        """Show colorful report"""
        print(Fore.CYAN + "\n🌤️ CURRENT WEATHER")
        print(Fore.YELLOW + "----------------------------")
        for key, val in info.items():
            print(Fore.GREEN + f"{key}: {val}")
        print(Fore.YELLOW + "----------------------------")

        print(Fore.CYAN + "\n📅 5-DAY FORECAST")
        print(Fore.YELLOW + "----------------------------")
        for day in forecast[:5]:
            print(
                Fore.MAGENTA
                + f"{day['Date']}: "
                + Fore.BLUE
                + f"{day['Avg Temp (°C)']}°C, "
                + Fore.LIGHTYELLOW_EX
                + f"{day['Main Weather']}"
            )
        print(Fore.YELLOW + "----------------------------")


def main():
    API_KEY = "_"  
    app = WeatherApp(API_KEY)

    print(Fore.CYAN + "\n🌦️ Welcome to the Weather CLI App (5-Day Forecast Edition)")
    print(Fore.YELLOW + "Type 'exit' anytime to quit.\n")

    while True:
        city = input(Fore.WHITE + "Enter city name: ")
        if city.lower() == "exit":
            print(Fore.CYAN + "👋 Goodbye! Stay weather-smart.\n")
            break

        current = app.get_current_weather(city)
        forecast = app.get_forecast(city)

        if current and forecast:
            current_info = app.parse_current(current)
            forecast_info = app.parse_forecast(forecast)
            app.display_weather(current_info, forecast_info)
            app.save_to_file({"Current": current_info, "Forecast": forecast_info})
        else:
            print(Fore.RED + "❌ Error: Could not fetch weather data. Check city name or API key.")


if __name__ == "__main__":
    main()