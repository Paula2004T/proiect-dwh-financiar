import datetime
from pymongo import MongoClient

class DataAccessLayer:
    def __init__(self, uri=""):
        self.client = MongoClient("mongodb+srv://paula_nou:ProiectDWH2026@cluster0.keyutkb.mongodb.net/?appName=Cluster0")
        self.db = self.client["dwh_financiar"]
        self.assets = self.db["assets"]
        self.data_sources = self.db["data_sources"]
        self.time_series = self.db["time_series"]

    def save_asset(self, asset_id: int, name: str, description: str, attributes: dict):
        doc = {
            "Asset_ID": asset_id,
            "Name": name,
            "Description": description,
            "System_Date": datetime.datetime.utcnow(),
            "Attributes": attributes,
            "deleted": False
        }
        self.assets.insert_one(doc)
        return doc

    def find_latest_asset(self, asset_id: int):
        pipeline = [
            {"$match": {"Asset_ID": asset_id}},
            {"$sort": {"System_Date": -1}},
            {"$limit": 1}
        ]
        res = list(self.assets.aggregate(pipeline))
        if res and not res[0].get("deleted", False):
            return res[0]
        return None

    def find_all_assets(self, limit: int = 10, offset: int = 0):
        pipeline = [
            {"$sort": {"System_Date": -1}},
            {"$group": {
                "_id": "$Asset_ID",
                "latest": {"$first": "$$ROOT"}
            }},
            {"$match": {"latest.deleted": False}},
            {"$skip": offset},
            {"$limit": limit}
        ]
        return [item["latest"] for item in self.assets.aggregate(pipeline)]

    def delete_asset(self, asset_id: int):
        doc = {
            "Asset_ID": asset_id,
            "System_Date": datetime.datetime.utcnow(),
            "deleted": True
        }
        self.assets.insert_one(doc)

    def save_time_series(self, asset_id: int, data_source_id: int, business_date: str, values_double: dict):
        b_date = datetime.datetime.strptime(business_date, "%Y-%m-%d")
        doc = {
            "Asset_ID": asset_id,
            "Data_Source_ID": data_source_id,
            "Business_Date": b_date,
            "System_Date": datetime.datetime.utcnow(),
            "Values_Double": values_double
        }
        self.time_series.insert_one(doc)
        return doc

  
    def find_time_series_range(self, asset_id: int, data_source_id: int, start_date: str, end_date: str, limit: int = 100, offset: int = 0):
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        
        pipeline = [
            {
                "$match": {
                    "Asset_ID": asset_id,
                    "Data_Source_ID": data_source_id,
                    "Business_Date": {"$gte": start, "$lte": end}
                }
            },
            {"$sort": {"Business_Date": -1, "System_Date": -1}},
            {
                "$group": {
                    "_id": "$Business_Date",
                    "latest": {"$first": "$$ROOT"}
                }
            },
            {"$sort": {"_id": 1}},
            {"$skip": offset},
            {"$limit": limit}
        ]
        return [item["latest"] for item in self.time_series.aggregate(pipeline)]