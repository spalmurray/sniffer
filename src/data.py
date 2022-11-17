from pymongo.mongo_client import MongoClient 
from bson.objectid import ObjectId

class Client:
    """Data access interface for MongoDB database for use with sniffer.

    The database has collections this collection:

    urls:
        - _id
        - url
        - interval
        - previous-data
        - guild
        - channel
        - user
    """

    def __init__(self):
        """Initialize a new Client connected to the local MongoDB instance."""
        self.mongo = MongoClient()
        self.db = self.mongo.sniffer

    def add_url(
        self, 
        url: str, 
        interval: str, 
        previous_data: str, 
        guild: int, 
        channel: int, 
        user: int
    ):
        url = {
            "url": url,
            "interval": interval,
            "previous_data": previous_data,
            "guild": guild,
            "channel": channel,
            "user": user
        }
        self.db.urls.insert_one(url)
    
    def update_data(self, id: str, new_data: str):
        self.db.urls.find_one_and_update(
            {"_id": ObjectId(id)}, update={"$set": {"previous_data": new_data}}
        )

    def delete_url(self, id: str, guild: int):
        url = self.db.urls.find_one_and_delete(
            {'_id': ObjectId(id), 'guild': guild}
        )
        return bool(url)
    
    def list_channel_urls(self, channel: int):
        cursor = self.db.urls.find({'channel': channel})
        urls = []
        for url in cursor:
            urls.append({"id": str(url["_id"]), "url": url["url"], "interval": url["interval"], "user": int(url["user"])})
        return urls

    def list_guild_urls(self, guild: int):
        cursor = self.db.urls.find({'guild': guild})
        urls = []
        for url in cursor:
            urls.append({"id": str(url["_id"]), "url": url["url"], "interval": url["interval"], "user": int(url["user"])})
        return urls
    
    def list_interval_matches(self, interval: str):
        cursor = self.db.urls.find({'interval': interval})
        return [url for url in cursor]
        