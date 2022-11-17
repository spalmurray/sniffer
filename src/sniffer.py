import requests

class Sniffer():
    def sniff(self, url: str):
        try:
            response = requests.get(url, timeout=1)
        except:
            return False
        return response.text
