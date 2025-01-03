import os
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
from langdetect import detect
import streamlit as st
import tempfile
import time

# Load environment variables
load_dotenv()

# Configure the Gemini API with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define generation config
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=safety_settings,
    generation_config=generation_config,
    system_instruction="You are an expert chatbot capable of assisting humans in various languages. "
                       "Your task is to engage in conversations across different languages, translate language, "
                       "answer queries, and provide helpful responses. Simplify complex topics, provide relatable "
                       "examples, and ensure responses remain culturally relevant.",
)

# Start a chat session
chat_session = model.start_chat(history=[])

def generate_audio_response(text, language="en"):
    """Generate an audio file from text using gTTS."""
    try:
        tts = gTTS(text, lang=language, slow=False)
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio_file.name)
        return temp_audio_file.name
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None

# Streamlit app configuration
st.set_page_config(page_title="Voice Assistant Chatbot", layout="centered")
st.markdown(
    """
    <style>
    :root {
        --primary-color: #4CAF50;
        --background-light: #FFFFFF;
        --background-dark: #1E1E1E;
        --text-light: #000000;
        --text-dark: #000000; /* Ensure text is black */
    }
    .main {
        background-color: var(--background-light);
        color: var(--text-light);
    }
    .dark-theme .main {
        background-color: var(--background-dark);
        color: var(--text-dark);
    }
    .chat-container {
        background: var(--background-light);
        color: var(--text-dark); /* Ensure chat container text is black */
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.5s ease-in-out;
    }
    .dark-theme .chat-container {
        background: var(--background-dark);
        color: var(--text-dark);
    }
    .user-message {
        background: #e0f7fa;
        border-radius: 15px;
        padding: 10px;
        margin: 10px 0;
        animation: slideInRight 0.5s ease-in-out;
        color: var(--text-dark); /* Ensure user messages are in black */
    }
    .bot-message {
        background: #e8eaf6;
        border-radius: 15px;
        padding: 10px;
        margin: 10px 0;
        animation: slideInLeft 0.5s ease-in-out;
        color: var(--text-dark); /* Ensure bot messages are in black */
    }
    .message-header {
        font-weight: bold;
    }
    .bot-avatar {
        display: inline-block;
        vertical-align: top;
        margin-right: 10px;
    }
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
        }
        to {
            transform: translateX(0);
        }
    }
    @keyframes slideInLeft {
        from {
            transform: translateX(-100%);
        }
        to {
            transform: translateX(0);
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔊 Voice Assistant Chatbot 🤖")
st.subheader("💬 Chat, 🧠 Listen, and 📚 Learn!")
st.write(
    "Welcome to the enhanced Voice Assistant Chatbot with animations! "
    "Type your messages below to interact with the bot and listen to its responses."
)

# Chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here 👇", "")
    submit = st.form_submit_button("Send ✈️")

# Process user input
if submit and user_input:
    with st.spinner("Preparing to amaze you... 🤖"):
        time.sleep(1)  # Simulate typing delay

        # Detect language
        try:
            detected_language = detect(user_input)
        except Exception as e:
            st.error(f"Error detecting language: {e}")
            detected_language = "en"

        # Send input to chatbot
        response = chat_session.send_message(user_input)
        model_response = response.text

        # Save the response in history
        st.session_state.history.append({"role": "user", "message": user_input})
        st.session_state.history.append({"role": "bot", "message": model_response})

        # Generate audio response
        audio_file_path = generate_audio_response(model_response, detected_language)

    # Display bot's response
    st.markdown(
        f"""
        <div class="chat-container">
            <div class="user-message">
                <div class="message-header">You:</div>
                <div>{user_input}</div>
            </div>
            <div class="bot-message">
                <img class="bot-avatar" src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png" width="30">
                <div class="message-header">Bot:</div>
                <div>{model_response}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Play audio if available
    if audio_file_path:
        audio_bytes = open(audio_file_path, "rb").read()
        st.audio(audio_bytes, format="audio/mp3")

# Display full chat history
st.write("### Chat History")
for message in st.session_state.history:
    if message["role"] == "user":
        st.markdown(f"<div class='user-message'><b>You:</b> {message['message']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            f"""
            <div class='bot-message'>
                <img class='bot-avatar' src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png" width="20">
                <b>Bot:</b> {message['message']}
            
            """,
            unsafe_allow_html=True,
        )

# Chat cleanup
if len(st.session_state.history) > 50:
    st.session_state.history = st.session_state.history[-50:]
