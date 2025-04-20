import requests
import json
import os

API_COUNTRIES = "https://countriesnow.space/api/v0.1/countries/positions"
API_CITIES = "https://countriesnow.space/api/v0.1/countries/cities"

OUTPUT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "app", "static", "data", "countries.json")
)

def fetch_countries():
    response = requests.get(API_COUNTRIES)
    response.raise_for_status()
    data = response.json()
    return [country["name"] for country in data["data"]]

def fetch_cities(country):
    response = requests.post(API_CITIES, json={"country": country})
    if response.status_code != 200:
        return []
    data = response.json()
    return data.get("data", [])

def build_country_city_map():
    country_list = fetch_countries()
    result = []

    for i, country in enumerate(country_list):
        print(f"[{i + 1}/{len(country_list)}] Fetching cities for: {country}")
        cities = fetch_cities(country)
        if cities:
            result.append({
                "country": country,
                "cities": cities
            })

    return result

def save_to_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Saved {len(data)} countries to {path}")

def main():
    try:
        data = build_country_city_map()
        save_to_json(data, OUTPUT_PATH)
    except Exception as e:
        print("❌ Error occurred:", e)

if __name__ == "__main__":
    main()
