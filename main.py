from fastapi import FastAPI
from pymongo import MongoClient
from bson.objectid import ObjectId
import google.generativeai as genai

# 1. Inițializăm aplicația (serverul) API
app = FastAPI(title="Acme Ltd Financial Data Warehouse")
# 2. Conectarea la baza de date
MONGO_URI = "mongodb+srv://paulatarau04_db_user:elmo@cluster0.keyutkb.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["acme_dwh"]
assets_collection = db["financial_assets"]
time_series_collection = db["time_series"]
# 3. Creăm prima noastră rută (endpoint) pentru Use Case 2 - [Q1]
@app.get("/assets")
def get_all_assets():
    """
    Returnează o listă cu toate instrumentele financiare din baza de date.
    """
    toate_activele = []
    for asset in assets_collection.find():
        asset["_id"] = str(asset["_id"])
        toate_activele.append(asset)
        
    return {"status": "success", "data": toate_activele}
@app.get("/")
def home():
    return {"message": "Bun venit la Data Warehouse-ul Acme Ltd!"}

# [Q2] Detaliile unui activ specific (căutare după ID)
@app.get("/assets/{asset_id}")
def get_asset_by_id(asset_id: str):
    try:
        
        asset = assets_collection.find_one({"_id": ObjectId(asset_id)})
        if asset:
            asset["_id"] = str(asset["_id"]) 
            return {"status": "success", "data": asset}
        else:
            return {"status": "error", "message": "Instrumentul nu a fost găsit."}
    except:
        return {"status": "error", "message": "ID-ul introdus nu este valid."}

# [Q3] Sursele de date (Data Providers)
@app.get("/sources")
def get_data_sources():
    surse = assets_collection.distinct("data_source")
    return {"status": "success", "data": surse}


import requests # Ne asigurăm că e importat pentru a prelua date


# Ruta specială pentru INGERAREA datelor istorice (UC1)
@app.get("/ingest-history")
def ingest_history():
    # 1. Găsim instrumentul BTC în baza de date pentru a-i lua ID-ul
    btc_asset = assets_collection.find_one({"symbol": "BTC"})
    if not btc_asset:
        return {"status": "error", "message": "Nu am găsit BTC în baza de date!"}
        
    # 2. Cerem istoricul prețului pe ultimele 5 zile de la API-ul CoinGecko
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=5"
    response = requests.get(url)
    date_istorice = response.json()
    
    # 3. Pregătim lista de înregistrări (time series)
    inregistrari_noi = []
    for price_data in date_istorice["prices"]:
        timestamp = price_data[0] 
        price = price_data[1]    
    
        inregistrare = {
            "asset_id": str(btc_asset["_id"]), 
            "data_source": "CoinGecko API",
            "indicator": "price_usd",
            "timestamp_ms": timestamp,
            "value": price
        }
        inregistrari_noi.append(inregistrare)
    
    if inregistrari_noi:
        time_series_collection.insert_many(inregistrari_noi)
        
    return {
        "status": "success", 
        "message": f"Am salvat {len(inregistrari_noi)} puncte de date istorice pentru BTC."
    }

# [Q4] Detalii despre o sursă de date (Data Provider)
@app.get("/sources/{source_name}")
def get_source_details(source_name: str):
    count_puncte = time_series_collection.count_documents({"data_source": source_name})
    
    if count_puncte > 0:
        return {
            "status": "success",
            "data": {
                "source_identifier": source_name,
                "description": f"Furnizor extern de date financiare ({source_name})",
                "total_time_series_points": count_puncte
            }
        }
    return {"status": "error", "message": "Sursa nu a fost găsită."}

# [Q5] Returnează seriile de timp pentru un activ și o sursă
@app.get("/timeseries")
def get_time_series(asset_id: str, data_source: str):
    """
    Exemplu de folosire în browser: 
    /timeseries?asset_id=ID_UL_AICI&data_source=CoinGecko API
    """
    query = {
        "asset_id": asset_id, 
        "data_source": data_source
    }
    rezultate = []
    for punct in time_series_collection.find(query, {"_id": 0}):
        rezultate.append(punct)   
    return {
        "status": "success", 
        "count": len(rezultate), 
        "data": rezultate
    }
# [UC 3] Data Aggregation & Analytics (Statistici de bază)
@app.get("/analytics/summary")
def get_analytics_summary(asset_id: str, data_source: str):
    """
    Returnează statistici (min, max, average) pentru o serie de timp.
    Exemplu de folosire: /analytics/summary?asset_id=ID_UL_AICI&data_source=CoinGecko API
    """
    query = {"asset_id": asset_id, "data_source": data_source}
    preturi = []
    for punct in time_series_collection.find(query):
        preturi.append(punct["value"])
    if not preturi:
        return {"status": "error", "message": "Nu am găsit date pentru a face analiza."}
    pret_minim = min(preturi)
    pret_maxim = max(preturi)
    pret_mediu = sum(preturi) / len(preturi)
    trend = "Crescător (Bullish)" if preturi[-1] > preturi[0] else "Descrescător (Bearish)"
    return {
        "status": "success",
        "analytics": {
            "numar_inregistrari_analizate": len(preturi),
            "pret_minim": round(pret_minim, 2),
            "pret_maxim": round(pret_maxim, 2),
            "pret_mediu": round(pret_mediu, 2),
            "trend_perioada": trend
        }
    }

# [UC 4] Integrare Asistent AI (LLM cu Function Calling / Tools)
GOOGLE_API_KEY = "AIzaSyBiYhq6RwgRe-KzFuC2b9_20Vb0O4_Hqh0"
genai.configure(api_key=GOOGLE_API_KEY)
def listeaza_active_disponibile():
    """Returnează lista cu toate instrumentele financiare disponibile în baza de date."""
    active = []
    for asset in assets_collection.find():
        active.append(f"{asset['description']} (Simbol: {asset['symbol']}, ID: {str(asset['_id'])})")
    return active
def obtine_statistici_pret(simbol: str):
    """Returnează informații statistice despre prețul unui activ (ex: BTC)."""
    asset = assets_collection.find_one({"symbol": simbol.upper()})
    if not asset:
        return f"Nu am găsit instrumentul {simbol} în baza de date."
    
    preturi = [p["value"] for p in time_series_collection.find({"asset_id": str(asset["_id"])})]
    if not preturi:
        return f"Nu avem istoric de prețuri pentru {simbol}."
        
    return f"Pentru {simbol}: preț minim = {min(preturi)}, maxim = {max(preturi)}, preț mediu = {sum(preturi)/len(preturi)}."

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', 
    tools=[listeaza_active_disponibile, obtine_statistici_pret],
    system_instruction="Ești un asistent financiar pentru platforma Acme Ltd. Răspunde la întrebări DOAR folosind informațiile obținute din uneltele (tools) pe care le ai la dispoziție. Dacă utilizatorul întreabă ceva ce nu poate fi aflat prin unelte, spune că nu ai aceste date."
)
@app.get("/chat")
def chat_cu_asistentul(mesaj: str):
    try:chat = model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(mesaj)
        
        return {
            "status": "success", 
            "intrebare": mesaj, 
            "raspuns_ai": response.text
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}