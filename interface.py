import streamlit as st
import requests

# Setările paginii
st.set_page_config(page_title="Acme Financial AI", page_icon="💰")

st.title("💰 Acme Ltd - Financial Assistant")
st.markdown("Întreabă asistentul AI despre activele din baza de date (ex: Bitcoin, Tesla).")

# 1. Sidebar pentru status
st.sidebar.header("Status Sistem")
if st.sidebar.button("Verifică conexiunea"):
    try:
        response = requests.get("http://127.0.0.1:8000/")
        st.sidebar.success("Conectat la serverul API!")
    except:
        st.sidebar.error("Serverul API nu este pornit.")

# 2. Zona de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afișăm istoricul conversației
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Căsuța de input
if prompt := st.chat_input("Ex: Care este prețul maxim pentru BTC?"):
    # Adăugăm întrebarea utilizatorului în chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Trimitem întrebarea către serverul tău de FastAPI
    with st.chat_message("assistant"):
        with st.spinner("Asistentul gândește..."):
            try:
                # Apelăm ruta /chat pe care am făcut-o împreună
                url = f"http://127.0.0.1:8000/chat?mesaj={prompt}"
                res = requests.get(url).json()
                raspuns = res["raspuns_ai"]
                st.markdown(raspuns)
                st.session_state.messages.append({"role": "assistant", "content": raspuns})
            except:
                st.error("Eroare: Asigură-te că serverul uvicorn rulează!")