import requests

url = "https://api.themoviedb.org/3/movie/63?api_key=YOUR_API_KEY&language=en-US"

session = requests.Session()
session.trust_env = False

response = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)

print(response.status_code)
print(response.json()["title"])