import requests

class Sniffer():
    def sniff(self, url: str):
        try:
            response = requests.get(url, timeout=2)
        except:
            return False
        return response.text
