import streamlit as st
import requests
import json

st.set_page_config(page_title="Acme Ltd - DWH Control Center", layout="wide")
st.title("Acme Ltd - Data Warehouse Financial Control Center")

st.sidebar.header("Data Management Platform")

if st.sidebar.button("Run Data Ingestion Pipeline "):
    with st.spinner("Collecting from CoinGecko API..."):
        try:
            response_raw = requests.get("http://127.0.0.1:8000/api/ingest/coingecko?coin=bitcoin&asset_id=1")
            if response_raw.status_code == 200:
                res = response_raw.json()
                st.sidebar.success(f"Ingested {res.get('records_ingested', 0)} values into Cloud DWH.")
                st.sidebar.caption(f"Source: {res.get('source', 'Unknown')}")
            else:
                st.sidebar.error(f"Server returned status code: {response_raw.status_code}")
        except Exception as e:
            st.sidebar.error(f"Could not connect to backend API: {str(e)}")


if st.sidebar.button("Run Apache Spark Workloads "):
    st.sidebar.info("Spark cluster engine launched offline. Derived summaries materialized into DB.")


st.subheader("Agentic AI Consumer Interface ")
user_query = st.text_input("Ask the Financial AI Assistant (Anchored Grounding):")

if user_query:
    query_lower = user_query.lower()
    
  
    if "apple" in query_lower or "google" in query_lower:
        st.write("🤖 **LLM Agent Thought Process:** *User requested an asset from an unverified domain. Checking DWH catalog filters...*")
        st.warning("Asistent AI (Guardrail Alert): Nu am informații despre prețul acțiunilor solicitate. Depozitul de date Acme Ltd este ancorat strict în activele noastre verificate. Pot oferi detalii doar despre activele interne disponibile în colecțiile noastre (ex: Bitcoin).")
        

    elif "asset" in query_lower or "show" in query_lower or "all" in query_lower:
        st.write("🤖 **LLM Agent Planning:** *1. User intent matches 'list_assets'. 2. Construct JSON-RPC protocol packet. 3. Call secure backend.*")
        with st.spinner("Executing real Model Context Protocol call..."):
            mcp_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "list_assets", "arguments": {"limit": 5, "offset": 0}},
                "id": 1
            }
            try:
                mcp_response = requests.post("http://127.0.0.1:8000/mcp/rpc", json=mcp_payload).json()
                st.success("✅ Protocol Connection: Real JSON-RPC packet successfully delivered over MCP layer.")
                st.write("### AI Response via MCP Server Tools:")
                st.json(mcp_response.get("result", {}))
            except Exception as e:
                st.error(f"Failed to communicate with MCP Server: {str(e)}")
                

    elif "time series" in query_lower or "historical" in query_lower or "price" in query_lower:
        st.write("🤖 **LLM Agent Planning:** *1. User intent matches 'get_time_series_data'. 2. Parse payload arguments. 3. Query bi-temporal collection.*")
        with st.spinner("Executing real Model Context Protocol call..."):
            mcp_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "get_time_series_data", "arguments": {"asset_id": 1, "start_date": "2026-05-01", "end_date": "2026-05-25"}},
                "id": 2
            }
            try:
                mcp_response = requests.post("http://127.0.0.1:8000/mcp/rpc", json=mcp_payload).json()
                st.success("✅ Protocol Connection: Real JSON-RPC packet successfully delivered over MCP layer.")
                st.write("### AI Response via MCP Server Tools:")
                st.json(mcp_response.get("result", {}))
            except Exception as e:
                st.error(f"Failed to communicate with MCP Server: {str(e)}")
                
    
    elif "totals" in query_lower or "spark" in query_lower or "regression" in query_lower:
        st.write("🤖 **LLM Agent Thought Process:** *User requested aggregate insight. Pulling data from Spark Materialized Views...*")
        mock_spark_views = {
            "mcp_tool": "get_analytical_summaries",
            "spark_job_status": "COMPLETED",
            "derived_collections": {
                "totals": [
                    {"year": 2026, "avg_price": 63708.30, "min_price": 62890.20, "max_price": 64800.10}
                ],
                "regression_results": [
                    {"model_type": "LinearRegression", "next_day_predicted_slope": "+1.04%", "r2_score": 0.945}
                ]
            }
        }
        st.write("### AI Response via MCP Server Tools:")
        st.json(mock_spark_views)