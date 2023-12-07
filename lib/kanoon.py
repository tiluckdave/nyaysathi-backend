import requests
import json

baseurl = "https://api.indiankanoon.org/"
headers = {
    'Authorization': 'Token 8299086305110a58718ff6dc38ebc4e36b6e2b02'
}

def searchKanoon(query):
    try:
        url = f"search/?formInput={query}+doctypes:act"
        response = requests.request("POST", baseurl + url, headers=headers)
        docs = response.json()['docs']
        return docs
    except Exception as e:
        print(e)
        return False
    
def getDocument(docId):
    try:
        url = f"doc/{docid}/"
        response = requests.request("POST", baseurl + url, headers=headers)
        return response.json()['doc']
    except Exception as e:
        print(e)
        return False