import streamlit as st
import asyncio
import edge_tts
import requests
import base64

# --- Sarvam AI Premium Logic ---
def generate_sarvam_voice(text, speaker, api_key):
    url = "https://api.sarvam.ai/text-to-speech"
    payload = {
        "inputs": [text],
        "target_language_code": "te-IN",
        "speaker": speaker,
        "model": "bulbul:v1"
    }
    headers = {"api-subscription-key": api_key, "Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            audio_content = response.json()["audios"][0]
            return base64.b64decode(audio_content)
        else:
            st.error(f"Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# --- Edge-TTS Free Logic ---
async def generate_free_voice(text, voice_type):
    voice = "te-IN-MohanNeural" if voice_type == "Male" else "te-IN-ShrutiNeural"
    # Using a slight slow-down for more natural feel
    communicate = edge_tts.Communicate(text, voice, rate="-5%")
    await communicate.save("free_voice.mp3")
    return "free_voice.mp3"

# --- UI Setup ---
st.set_page_config(page_title="Telugu Pro Narrator", page_icon="🎙️")
st.title("🎙️ Telugu AI Voice Pro")

st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Sarvam API Key", type="password")
st.sidebar.markdown("[Get Key Here](https://dashboard.sarvam.ai/)")

engine = st.radio("Choose Engine", ["Premium (Natural Voices)", "Standard (Free Backup)"], horizontal=True)

script = st.text_area("Telugu Script", placeholder="ఇక్కడ మీ కథను పేస్ట్ చేయండి...", height=250)

if engine == "Premium (Natural Voices)":
    # Sarvam has excellent distinct voices
    speaker = st.selectbox("Select Natural Speaker", ["mahesh", "arvind", "meera", "pavithra"])
    if not api_key:
        st.info("💡 Please enter your API key in the sidebar to use Natural voices.")
else:
    speaker = st.selectbox("Select Backup Voice", ["Male", "Female"])

if st.button("Generate Narration", type="primary"):
    if not script:
        st.warning("Please enter text.")
    else:
        with st.spinner("Creating voiceover..."):
            if engine == "Premium (Natural Voices)":
                if api_key:
                    audio_data = generate_sarvam_voice(script, speaker, api_key)
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
