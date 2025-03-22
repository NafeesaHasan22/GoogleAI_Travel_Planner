import streamlit as st
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
import requests
from PIL import Image
import base64

# Constants
GMAPS_DIRECTIONS_API_URL = "https://maps.googleapis.com/maps/api/directions/json"
GMAPS_STATIC_MAP_API_URL = "https://maps.googleapis.com/maps/api/staticmap"

# Configure API Keys
with open(r"C:\Users\nafeesa hasan\Downloads\KEYS\google_api.txt") as f:
    api_key = f.read().strip()

genai.configure(api_key=api_key)

with open(r"C:\Users\nafeesa hasan\Downloads\KEYS\Google _Map_ API.txt") as f:
    gmaps_api_key = f.read().strip()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=api_key)

# Prompt templates
prompt_template = PromptTemplate(
    input_variables=["source", "destination"],
    template="""
    You are an AI travel assistant. Provide the best travel options from {source} to {destination}.
    Include different travel modes (cab, bus, train, flight) with estimated costs.
    Also include estimated travel duration for each mode. Format the response in a structured manner.
    """
)
llm_chain = LLMChain(llm=llm, prompt=prompt_template)

tips_prompt = PromptTemplate(
    input_variables=["destination"],
    template="""
    Suggest 3 travel safety or planning tips for someone visiting {destination}.
    """
)
tips_chain = LLMChain(llm=llm, prompt=tips_prompt)

def get_travel_recommendations(source, destination):
    return llm_chain.run({"source": source, "destination": destination})

def get_travel_tips(destination):
    return tips_chain.run({"destination": destination})

def get_live_travel_data(source, destination, mode):
    try:
        params = {
            "origin": source,
            "destination": destination,
            "key": gmaps_api_key,
            "mode": mode,
        }
        response = requests.get(GMAPS_DIRECTIONS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data["status"] != "OK":
            return {"Error": data.get("error_message", "No valid route found.")}

        route = data["routes"][0]["legs"][0]
        return {
            mode.capitalize(): {
                "price": "$30 - $50 (estimated)",
                "duration": route["duration"]["text"],
                "distance": route["distance"]["text"]
            }
        }
    except requests.exceptions.RequestException as e:
        return {"Error": f"Google Maps API Error: {e}"}
    except ValueError as e:
        return {"Error": f"Invalid response: {e}"}

def add_styling():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to right, #e3f2fd, #ffffff);
            font-family: 'Segoe UI', sans-serif;
        }
        .title {
            font-size: 2.8rem;
            color: #0d47a1;
        }
        .subtitle {
            color: #1565c0;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="AI-Powered Travel Planner", layout="wide")
    add_styling()
    st.markdown("<h1 class='title'>✈️ AI-Powered Travel Planner</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Plan smarter. Travel better. Get personalized routes and tips powered by AI.</p>", unsafe_allow_html=True)

    with st.form("travel_form"):
        source = st.text_input("🌍 Enter Source Location")
        destination = st.text_input("📍 Enter Destination Location")
        mode = st.selectbox("🛣️ Choose Travel Mode", ["driving", "walking", "bicycling", "transit"])
        submitted = st.form_submit_button("🔍 Get Travel Recommendations")

    if submitted:
        if source and destination:
            with st.spinner("Fetching smart travel suggestions ✨"):
                travel_info = get_travel_recommendations(source, destination)
                travel_tips = get_travel_tips(destination)
                live_data = get_live_travel_data(source, destination, mode)

                st.markdown("### 🗺️ Recommended Travel Options")
                st.success(travel_info)

                st.markdown("### 🚦 Live Travel Info (Google Maps)")
                for mode_name, details in live_data.items():
                    st.info(f"**{mode_name}** → Cost: {details.get('price')}, Duration: {details.get('duration')}, Distance: {details.get('distance')}")

                st.markdown("### 💡 Travel Tips")
                st.warning(travel_tips)

                map_url = f"{GMAPS_STATIC_MAP_API_URL}?size=600x300&markers={source}&markers={destination}&path={source}|{destination}&key={gmaps_api_key}"
                st.image(map_url, caption="🗺️ Route Map Preview")
        else:
            st.error("Please enter both source and destination to continue.")

if __name__ == "__main__":
    main()
