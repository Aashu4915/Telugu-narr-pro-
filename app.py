import streamlit as st
import asyncio
import edge_tts
import requests
import base64
import json

# --- Sarvam AI Premium Logic ---
def generate_sarvam_voice(text, speaker, api_key):
    url = "https://api.sarvam.ai/text-to-speech"
    api_key = api_key.strip()
    
    payload = {
        "inputs": [text],
        "target_language_code": "te-IN",
        "speaker": speaker,
        "model": "bulbul:v3"
    }
    
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json; charset=utf-8"
    }

    try:
        response = requests.post(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers=headers
        )
        
        if response.status_code == 200:
            audio_content = response.json()["audios"][0]
            return base64.b64decode(audio_content)
        else:
            st.error(f"Sarvam API Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# --- Edge-TTS Free Logic ---
async def generate_free_voice(text, voice_type):
    voice = "te-IN-MohanNeural" if voice_type == "Male" else "te-IN-ShrutiNeural"
    communicate = edge_tts.Communicate(text, voice, rate="-5%")
    await communicate.save("free_voice.mp3")
    return "free_voice.mp3"

# --- UI Setup ---
st.set_page_config(page_title="Telugu Pro Narrator", page_icon="🎙️")
st.title("🎙️ Telugu AI Voice Pro")

st.sidebar.header("Configuration")
api_key_input = st.sidebar.text_input("Sarvam API Key", type="password")

engine = st.radio("Choose Engine", ["Premium (Natural Voices)", "Standard (Free Backup)"], horizontal=True)

script = st.text_area("Telugu Script", placeholder="ఇక్కడ మీ కథను పేస్ట్ చేయండి...", height=250)

if engine == "Premium (Natural Voices)":
    # These are the correct names for Bulbul v3 based on the error message
    # Categorized for easier choice
    male_voices = ["vijay", "aditya", "gokul", "mani", "shubh", "anand", "tarun", "sunny"]
    female_voices = ["shruti", "kavitha", "shreya", "roopa", "tanya", "priya", "neha", "pooja"]
    
    speaker = st.selectbox("Select Natural Speaker", male_voices + female_voices)
    
    if "vijay" in speaker or "aditya" in speaker:
        st.caption("Tip: Vijay and Aditya are great for serious narrations.")
    elif "shruti" in speaker or "kavitha" in speaker:
        st.caption("Tip: Shruti and Kavitha are great for stories.")

else:
    speaker = st.selectbox("Select Backup Voice", ["Male", "Female"])

if st.button("Generate Narration", type="primary"):
    if not script:
        st.warning("Please enter text.")
    else:
        with st.spinner("Creating voiceover..."):
            if engine == "Premium (Natural Voices)":
                if api_key_input:
                    audio_data = generate_sarvam_voice(script, speaker, api_key_input)
                    if audio_data:
                        st.audio(audio_data)
                        st.download_button("Download Pro MP3", audio_data, file_name="pro_narration.mp3")
                else:
                    st.error("API Key Required for Premium Engine.")
            else:
                audio_path = asyncio.run(generate_free_voice(script, speaker))
                st.audio(audio_path)
                with open(audio_path, "rb") as f:
                    st.download_button("Download Standard MP3", f, file_name="free_narration.mp3")
