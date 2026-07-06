import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class APIToolManager:
    """
    Central API Tool Manager.
    Executes all external API calls so Gemini never directly connects to the internet.
    Handles retries, caching, normalization, and graceful degradation on failure.
    Never crashes the application.
    """
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 1800  # Cache duration: 30 minutes
        
        # Configure robust retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            backoff_factor=1
        )
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_from_cache(self, cache_key: str):
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                print(f"[API Manager] Cache hit for {cache_key}")
                return data
        return None

    def _save_to_cache(self, cache_key: str, data: dict):
        self._cache[cache_key] = (data, time.time())

    def _execute_api_call(self, cache_key: str, url: str, params: dict, fallback_data: dict) -> dict:
        """
        Executes a network request with caching, retries, and graceful fallback.
        """
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        try:
            # If no API key is set in the environment, we intentionally fallback immediately
            # to avoid crashing or hanging on 401s during the hackathon/demo.
            if not os.environ.get("GOOGLE_API_KEY") and "google" in url:
                raise Exception("Missing API Key")

            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Normalize and cache
            normalized_data = {"status": "success", "source": "Live API", "data": data}
            self._save_to_cache(cache_key, normalized_data)
            return normalized_data

        except Exception as e:
            print(f"⚠️ [API Manager] Failed to fetch {cache_key} ({e}). Using normalized fallback.")
            normalized_fallback = {"status": "fallback", "source": "Simulated Data", "data": fallback_data}
            self._save_to_cache(cache_key, normalized_fallback)
            return normalized_fallback

    # --- Supported APIs ---

    def get_weather(self, location: str) -> dict:
        fallback = {"temperature": "22°C", "condition": "Clear", "impact": "Positive for retail foot traffic."}
        return self._execute_api_call(f"weather_{location}", "https://api.openweathermap.org/data/2.5/weather", {"q": location}, fallback)

    def get_google_maps(self, query: str) -> dict:
        fallback = {"location_type": "Commercial Hub", "foot_traffic": "High", "competitors_nearby": 4}
        return self._execute_api_call(f"maps_{query}", "https://maps.googleapis.com/maps/api/place/textsearch/json", {"query": query}, fallback)

    def get_news(self, topic: str) -> dict:
        fallback = {"headlines": [f"{topic} sector sees steady growth", "New regulations affect local markets"], "sentiment": "Neutral"}
        return self._execute_api_call(f"news_{topic}", "https://newsapi.org/v2/everything", {"q": topic}, fallback)

    def get_finance(self, symbol: str) -> dict:
        fallback = {"symbol": symbol, "trend": "Upward", "macro_economic_state": "Stable interest rates"}
        return self._execute_api_call(f"finance_{symbol}", "https://query1.finance.yahoo.com/v7/finance/quote", {"symbols": symbol}, fallback)

    def get_traffic(self, location: str) -> dict:
        fallback = {"congestion_level": "Moderate", "logistics_delay": "None", "road_closures": 0}
        return self._execute_api_call(f"traffic_{location}", "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json", {"point": location}, fallback)

    def get_business_trends(self, keyword: str) -> dict:
        fallback = {"search_volume": "Increasing", "seasonal_peak": "Upcoming in 2 months", "consumer_interest": 85}
        return self._execute_api_call(f"trends_{keyword}", "https://mock.trends.api", {"q": keyword}, fallback)

    def get_calendar(self) -> dict:
        fallback = {"upcoming_holidays": ["Summer Break", "Local Festival"], "business_days_remaining": 22}
        return self._execute_api_call("calendar_general", "https://www.googleapis.com/calendar/v3/calendars/en.usa#holiday@group.v.calendar.google.com/events", {}, fallback)

# Singleton Instance
api_tool_manager = APIToolManager()
