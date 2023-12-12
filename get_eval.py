import requests
import json


url = 'http://localhost:8080/analyze/'

def get_eval(fen, MultiPV=3, Depth=20):
    data = {
      "FEN": fen,
      "MultiPV": MultiPV,
      "Depth": Depth
    }
    json_data = json.dumps(data)
    response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json_data)
    print(response.text)
    return response.text