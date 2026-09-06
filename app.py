import streamlit as st
import asyncio
import edge_tts
import requests
import base64
import json

# --- Sarvam AI Premium Logic (Bulbul v3) ---
def generate_sarvam_voice(text, speaker, pace, temperature, api_key):
    url = "https://api.sarvam.ai/text-to-speech"
    api_key = api_key.strip()
    
    payload = {
        "inputs": [text],
        "target_language_code": "te-IN",
        "speaker": speaker,
        "model": "bulbul:v3",
        "pace": pace,
        "temperature": temperature
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
async def generate_free_voice(text, voice_type, rate, pitch):
    voice = "te-IN-MohanNeural" if voice_type == "Male" else "te-IN-ShrutiNeural"
    # Format: +0% or -5% for rate, +0Hz or -5Hz for pitch
    rate_str = f"{'+' if rate >= 0 else ''}{rate}%"
    pitch_str = f"{'+' if pitch >= 0 else ''}{pitch}Hz"
    
    communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
    await communicate.save("free_voice.mp3")
    return "free_voice.mp3"

# --- UI Setup ---
st.set_page_config(page_title="Telugu Voice Pro", page_icon="🎙️")
st.title("🎙️ Telugu AI Voice Pro")

# Sidebar
st.sidebar.header("Configuration")
api_key_input = st.sidebar.text_input("Sarvam API Key", type="password")

engine = st.radio("Choose Engine", ["Premium (Sarvam AI)", "Standard (Free Backup)"], horizontal=True)

# Main Text Input
script = st.text_area("Telugu Script", placeholder="ఇక్కడ మీ కథను పేస్ట్ చేయండి...", height=250)

# --- CHARACTER COUNTER ---
char_count = len(script)
limit = 2500 if engine == "Premium (Sarvam AI)" else 5000
color = "green" if char_count <= limit else "red"
st.markdown(f"<p style='text-align: right; color: {color};'>Characters: <b>{char_count}</b> / {limit}</p>", unsafe_allow_html=True)

# Advanced Settings
with st.expander("🛠️ Advanced Settings", expanded=True):
    col1, col2 = st.columns(2)
    
    if engine == "Premium (Sarvam AI)":
        with col1:
            # Bulbul v3 supports names from the error list we saw earlier
            males = ["vijay", "aditya", "gokul", "mani", "shubh", "anand", "tarun", "sunny"]
            females = ["shruti", "kavitha", "shreya", "roopa", "tanya", "priya", "neha", "pooja"]
            speaker = st.selectbox("Select Speaker", males + females)
            pace = st.slider("Speed (Pace)", 0.5, 2.0, 1.0, 0.1)
        with col2:
            st.write("") # Padding
            temp = st.slider("Expressiveness (Temperature)", 0.0, 1.0, 0.6, 0.1)
            st.caption("Tip: Higher temperature makes voice more 'emotional' and varied.")
    else:
        with col1:
            speaker = st.selectbox("Select Backup Voice", ["Male", "Female"])
            f_rate = st.slider("Speed Adjust (%)", -50, 50, 0)
        with col2:
            st.write("") # Padding
            f_pitch = st.slider("Pitch Adjust (Hz)", -20, 20, 0)

# Generate Button
if st.button("Generate Narration", type="primary"):
    if not script:
        st.warning("Please enter text.")
    elif char_count > limit:
        st.error(f"Text is too long! Please keep it under {limit} characters.")
    else:
        with st.spinner("Creating voiceover..."):
            if engine == "Premium (Sarvam AI)":
                if api_key_input:
                    audio_data = generate_sarvam_voice(script, speaker, pace, temp, api_key_input)
                    if audio_data:
                        st.audio(audio_data)
                        st.download_button("Download Pro MP3", audio_data, file_name="pro_narration.mp3")
                else:
                    st.error("API Key Required for Premium Engine (Check Sidebar).")
            else:
                audio_path = asyncio.run(generate_free_voice(script, speaker, f_rate, f_pitch))
                st.audio(audio_path)
                with open(audio_path, "rb") as f:
                    st.download_button("Download Standard MP3", f, file_name="free_narration.mp3")
