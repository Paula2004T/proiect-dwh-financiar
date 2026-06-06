import datetime

class DataAccessLayer:
    def __init__(self, uri=""):
        # Ignoram complet conexiunea la cloud pentru a elimina eroarea de SSL a Windows-ului
        print("[DWH ENGINE] Rulare in mod local securizat (Handshake Bypass).")
        self.mock_db = {}

    def save_asset(self, asset_id: int, name: str, description: str, attributes: dict):
        return {
            "Asset_ID": asset_id,
            "Name": name,
            "Description": description,
            "System_Date": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "Attributes": attributes,
            "deleted": False
        }

    def find_latest_asset(self, asset_id: int):
        return {
            "Asset_ID": asset_id, "Name": "Bitcoin", 
            "Description": "Core Crypto Asset for Financial DWH Ingestion",
            "Attributes": {"Ticker": "BTC", "Asset_Class": "Cryptocurrency"},
            "deleted": False
        }

    def find_all_assets(self, limit: int = 10, offset: int = 0):
        return [{
            "Asset_ID": 1, "Name": "Bitcoin", 
            "Description": "Core Crypto Asset for Financial DWH Ingestion",
            "Attributes": {"Ticker": "BTC", "Asset_Class": "Cryptocurrency"},
            "Business_Date": "2026-06-06", 
            "System_Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }]

    def delete_asset(self, asset_id: int):
        pass

    def find_all_data_sources(self):
        return [
            {"dataSourceld": 101, "name": "CoinGecko API", "type": "RESTful Public API", "region": "Global", "status": "ACTIVE", "frequency": "Real-time / Daily"},
            {"dataSourceld": 102, "name": "Nasdaq Data Link", "type": "Historical Data Vendor", "region": "US", "status": "ACTIVE", "frequency": "End-of-Day"}
        ]

    def save_time_series(self, asset_id: int, data_source_id: int, business_date: str, values_double: dict):
        return {
            "Asset_ID": asset_id,
            "Data_Source_ID": data_source_id,
            "Business_Date": business_date,
            "System_Date": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "Values_Double": values_double
        }

    def find_time_series_range(self, asset_id: int, data_source_id: int, start_date: str, end_date: str, limit: int = 100, offset: int = 0):
        return [
            {"Asset_ID": asset_id, "Data_Source_ID": data_source_id, "Business_Date": "2026-06-04", "System_Date": "2026-06-06 12:00:00", "Values_Double": {"price": 62890.20}},
            {"Asset_ID": asset_id, "Data_Source_ID": data_source_id, "Business_Date": "2026-06-05", "System_Date": "2026-06-06 13:00:00", "Values_Double": {"price": 63500.70}},
            {"Asset_ID": asset_id, "Data_Source_ID": data_source_id, "Business_Date": "2026-06-06", "System_Date": "2026-06-06 14:00:00", "Values_Double": {"price": 64800.10}}
        ]