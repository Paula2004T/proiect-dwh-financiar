import datetime
import certifi
from pymongo import MongoClient

class DataAccessLayer:
    def __init__(self, uri=""):
    
        connection_uri = "mongodb+srv://paula_nou:ProiectDWH2026@cluster0.keyutkb.mongodb.net/?appName=Cluster0"
        try:
            self.client = MongoClient(connection_uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
            self.db = self.client["dwh_financiar"]
            self.assets = self.db["assets"]
            self.data_sources = self.db["data_sources"]
            self.time_series = self.db["time_series"]
            
            if self.data_sources.count_documents({}) == 0:
                self.data_sources.insert_many([
                    {"dataSourceld": 101, "name": "CoinGecko API", "type": "RESTful Public API", "region": "Global", "status": "ACTIVE", "frequency": "Real-time / Daily"},
                    {"dataSourceld": 102, "name": "Nasdaq Data Link", "type": "Historical Data Vendor", "region": "US", "status": "ACTIVE", "frequency": "End-of-Day"}
                ])
        except Exception as e:
            print(f"[DAL ERROR] Conexiunea esuata: {str(e)}")

    def save_asset(self, asset_id: int, name: str, description: str, attributes: dict):
     
        doc = {
            "Asset_ID": asset_id,
            "Name": name,
            "Description": description,
            "Business_Date": datetime.date.today().strftime("%Y-%m-%d"),
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
        results = list(self.assets.aggregate(pipeline))
        return [item["latest"] for item in results]

    def delete_asset(self, asset_id: int):
     
        doc = {
            "Asset_ID": asset_id,
            "Business_Date": datetime.date.today().strftime("%Y-%m-%d"),
            "System_Date": datetime.datetime.utcnow(),
            "deleted": True
        }
        self.assets.insert_one(doc)

    def find_all_data_sources(self):
        return list(self.data_sources.find({}, {"_id": 0}))

    def save_time_series(self, asset_id: int, data_source_id: int, business_date: str, values_double: dict):
        b_date = datetime.datetime.strptime(business_date, "%Y-%m-%d")
        
        existing = self.time_series.find_one({
            "Asset_ID": asset_id,
            "Data_Source_ID": data_source_id,
            "Business_Date": b_date
        })
        if existing and existing.get("Values_Double") == values_double:
            return existing 
            
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
            {"$match": {
                "Asset_ID": asset_id,
                "Data_Source_ID": data_source_id,
                "Business_Date": {"$gte": start, "$lte": end}
            }},
            {"$sort": {"Business_Date": 1, "System_Date": -1}},
            {"$group": {
                "_id": "$Business_Date",
                "latest": {"$first": "$$ROOT"}
            }},
            {"$sort": {"_id": 1}},
            {"$skip": offset},
            {"$limit": limit}
        ]
        results = list(self.time_series.aggregate(pipeline))
        return [item["latest"] for item in results]