from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from dal import DataAccessLayer
import requests
import datetime

app = FastAPI(title="Acme Ltd - Financial DWH REST API & MCP Server")
dal = DataAccessLayer()

class AssetPayload(BaseModel):
    Asset_ID: int
    Name: str
    Description: str
    Attributes: Dict[str, str]

@app.get("/api/assets")
def get_assets(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    try:
        assets = dal.find_all_assets(limit=limit, offset=offset)
        for a in assets:
            if "_id" in a:
                a["_id"] = str(a["_id"])
            if "System_Date" in a and hasattr(a["System_Date"], "strftime"):
                a["System_Date"] = a["System_Date"].strftime("%Y-%m-%d %H:%M:%S")
        return {"data": assets, "limit": limit, "offset": offset}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assets/{asset_id}")
def get_asset_by_id(asset_id: int):
    asset = dal.find_latest_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found or deleted.")
    if "_id" in asset:
        asset["_id"] = str(asset["_id"])
    if "System_Date" in asset and hasattr(asset["System_Date"], "strftime"):
        asset["System_Date"] = asset["System_Date"].strftime("%Y-%m-%d %H:%M:%S")
    return asset

@app.get("/api/data-sources")
def get_data_sources():
    try:
        return {"data": dal.find_all_data_sources()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data-sources/{source_id}")
def get_data_source_by_id(source_id: int):
    sources = dal.find_all_data_sources()
    match = next((s for s in sources if s.get("dataSourceld") == source_id), None)
    if match:
        return match
    raise HTTPException(status_code=404, detail="Data source identifier not found.")

@app.get("/api/timeseries")
def get_time_series(asset_id: int, data_source_id: int, start_date: str, end_date: str, limit: int = 50, offset: int = 0):
    try:
        data = dal.find_time_series_range(asset_id, data_source_id, start_date, end_date, limit, offset)
        for d in data:
            if "_id" in d:
                d["_id"] = str(d["_id"])
            if hasattr(d["Business_Date"], "strftime"): 
                d["Business_Date"] = d["Business_Date"].strftime("%Y-%m-%d")
            if hasattr(d["System_Date"], "strftime"): 
                d["System_Date"] = d["System_Date"].strftime("%Y-%m-%d %H:%M:%S")
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/ingest/coingecko")
def trigger_ingestion(coin: str = "bitcoin", asset_id: int = 1):
    
    dal.save_asset(asset_id=asset_id, name=coin.capitalize(), description="Ingested via CoinGecko Public API", attributes={"Ticker": "BTC", "Asset_Class": "Cryptocurrency"})
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=5"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise Exception(f"CoinGecko API returned status {response.status_code}")
            
        raw_data = response.json()
        inserted_count = 0
        
        if "prices" in raw_data:
            for item in raw_data["prices"][:10]:
                timestamp_ms = item[0]
                price_value = item[1]
                business_date = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0).strftime("%Y-%m-%d")
                
             
                dal.save_time_series(asset_id=asset_id, data_source_id=101, business_date=business_date, values_double={"price": price_value})
                inserted_count += 1
                
        return {"status": "success", "records_ingested": inserted_count, "source": "Live CoinGecko API"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"External ingestion failed: {str(e)}")

@app.post("/mcp/rpc")
def mcp_rpc_endpoint(rpc_request: dict):
    method = rpc_request.get("method")
    params = rpc_request.get("params", {})
    rpc_id = rpc_request.get("id", 1)

    if method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": rpc_id,
            "result": {
                "tools": [
                    {"name": "list_assets", "description": "List financial assets stored inside DWH.", "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "get_time_series_data", "description": "Retrieve bitemporal time series records.", "inputSchema": {"type": "object", "properties": {"asset_id": {"type": "integer"}}}}
                ]
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        
        if tool_name == "list_assets":
     
            assets = dal.find_all_assets()
            for a in assets: a["_id"] = str(a["_id"]); a["System_Date"] = a["System_Date"].strftime("%Y-%m-%d %H:%M:%S")
            return {"jsonrpc": "2.0", "id": rpc_id, "result": {"content": [{"type": "text", "text": str(assets)}]}}
            
        elif tool_name == "get_time_series_data":
  
            today = datetime.date.today()
            start_str = (today - datetime.timedelta(days=10)).strftime("%Y-%m-%d")
            end_str = today.strftime("%Y-%m-%d")
            data = dal.find_time_series_range(asset_id=1, data_source_id=101, start_date=start_str, end_date=end_str)
            for d in data: d["_id"] = str(d["_id"]); d["Business_Date"] = d["Business_Date"].strftime("%Y-%m-%d"); d["System_Date"] = d["System_Date"].strftime("%Y-%m-%d %H:%M:%S")
            return {"jsonrpc": "2.0", "id": rpc_id, "result": {"content": [{"type": "text", "text": str(data)}]}}
            
    return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": "Method not found"}}