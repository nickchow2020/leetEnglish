from api_keys import wordsapi
from api_keys import serpapi
from serpapi import GoogleSearch
import requests

def get_english_def(vol):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{vol}/definitions"
    headers = {
        'x-rapidapi-key':wordsapi
    }
    response = requests.request("GET", url, headers=headers)
    data = response.json()
    return data["definitions"][0]

def get_definition_image(search):
  params = {
  "q": search,
  "tbm": "isch",
  "ijn": "0",
  "api_key": serpapi}

  search = GoogleSearch(params)
  results = search.get_dict()
  return results['images_results'][:20]

