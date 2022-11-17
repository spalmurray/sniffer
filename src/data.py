from pymongo.mongo_client import MongoClient 
from bson.objectid import ObjectId

class Client:
    """Data access interface for MongoDB database for use with sniffer.

    The database has collections this collection:

    urls:
        - _id
        - url
        - interval
        - previous_data
        - is_down
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
            "is_down": False,
            "guild": guild,
            "channel": channel,
            "user": user
        }
        self.db.urls.insert_one(url)
    
    def update_data(self, id: str, new_data: str):
        self.db.urls.find_one_and_update(
            {"_id": ObjectId(id)}, update={"$set": {"previous_data": new_data}}
        )

    def set_is_down(self, id: str, is_down: bool):
        self.db.urls.find_one_and_update(
            {"_id": ObjectId(id)}, update={"$set": {"is_down": is_down}}
        )

    def delete_url(self, id: str, guild: int):
        url = self.db.urls.find_one_and_delete(
            {'_id': ObjectId(id), 'guild': guild}
        )
        return bool(url)
    
    def list_channel_urls(self, channel: int):
        cursor = self.db.urls.find({'channel': channel})
        return [url for url in cursor]

    def list_guild_urls(self, guild: int):
        cursor = self.db.urls.find({'guild': guild})
        return [url for url in cursor]
    
    def list_interval_matches(self, interval: str):
        cursor = self.db.urls.find({'interval': interval})
        return [url for url in cursor]
    
    def run_migration(self):
        cursor = self.db.urls.find()
        for url in cursor:
            if "is_down" not in url.keys():
                self.set_is_down(url["_id"], False)
                


if __name__ == "__main__":
    database = Client()
    database.run_migration()
    print("done")