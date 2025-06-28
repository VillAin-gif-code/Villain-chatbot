import streamlit as st
import google.generativeai as genai
import requests

# --- Custom CSS for background and input styling ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        position: relative;
        background-image: url('https://wallpapercave.com/wp/FJi8AZ8.jpg');
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center center;
        min-height: 100vh;
    }
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.45);
        z-index: 0;
    }
    .stApp, .stTextInput, .stMarkdown, .stTitle, .stHeader, .stSubheader, .stCaption, .stDataFrame {
        color:  !important;
        position: relative;
        z-index: 1;
        font-size: 22px !important;
        font-weight: bold !important;
    }
    html, body, [data-testid="stAppViewContainer"], .stTextInput input, .stMarkdown, .stTitle, .stHeader, .stSubheader, .stCaption, .stDataFrame, .stChatMessageContent {
        font-size: 28px !important;
        font-weight: bold !important;
        color: #FFD700 !important;
        text-shadow: none !important;
        letter-spacing: 0.2px !important;
        line-height: 1.3 !important;
    }
    .stTextInput input, .stTextArea textarea {
        color: #111 !important;
        background: #fff !important;
    }
    .stButton button {
        background-color: #FFD700 !important;
        color: #111 !important;
        font-weight: bold !important;
        font-size: 22px !important;
        border-radius: 8px !important;
        padding: 0.5em 2em !important;
    }
    /* Hide the Ctrl+Enter message */
    div[data-testid="stTextArea"] div[role="alert"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("VillAin Chatbot")

# Sidebar for text size (hidden like a toolbar)
with st.sidebar:
    size = st.selectbox(
        "Choose text size:",
        ("Small", "Medium", "Large", "Extra Large"),
        index=1
    )

size_map = {
    "Small": "18px",
    "Medium": "22px",
    "Large": "28px",
    "Extra Large": "36px"
}

st.markdown(
    f"""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stTextInput input, .stTextArea textarea, .stMarkdown, .stTitle, .stHeader, .stSubheader, .stCaption, .stDataFrame, .stChatMessageContent {{
        font-size: {size_map[size]} !important;
        font-weight: bold !important;
        color: #111 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Replace with your actual keys
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash') # Use the correct model for your API key

# Initialize chat history in session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

def search_photo(query):
    url = f"https://api.unsplash.com/search/photos?query={query}&client_id={UNSPLASH_ACCESS_KEY}&per_page=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']
    return None

def colored_markdown(text, color, bold=False, italic=False):
    style = f"color:{color}; font-size:22px;"
    if bold:
        style += " font-weight:bold;"
    if italic:
        style += " font-style:italic;"
    st.markdown(f'<span style="{style}">{text}</span>', unsafe_allow_html=True)

def send_message():
    user_input = st.session_state.get("user_input", "")
    if user_input:
        # Detect image request
        if "image" in user_input.lower() or "photo" in user_input.lower():
            subject = user_input.lower().replace("image", "").replace("photo", "").strip()
            img_url = search_photo(subject)
            st.session_state.messages.append(("Villain", user_input))
            if img_url:
                st.session_state.messages.append(("AI Sidekick", f"Here is an image of {subject}:"))
                st.session_state.messages.append(("Image", img_url))
            else:
                st.session_state.messages.append(("AI Sidekick", "Sorry, I couldn't find an image."))
        else:
            response = st.session_state.chat.send_message(user_input)
            st.session_state.messages.append(("Villain", user_input))
            st.session_state.messages.append(("AI Sidekick", response.text))

def formatted_markdown(line):
    stripped = line.strip()
    # If line starts with a number and a dot, just show it (no bullet)
    if stripped and stripped[0].isdigit() and stripped[1:3] == ". ":
        colored_markdown(stripped, "#FFD700")
    # Bold bullet point: ** at start and end
    elif stripped.startswith("**") and stripped.endswith("**"):
        content = "• " + stripped.strip("*")
        colored_markdown(content, "#FFD700", bold=True)
    # Italic bullet point: * at start and end
    elif stripped.startswith("*") and stripped.endswith("*"):
        content = "• " + stripped.strip("*")
        colored_markdown(content, "#FFD700", italic=True)
    # Line starts with "* " (just remove the "* ")
    elif stripped.startswith("* "):
        content = stripped[2:]
        colored_markdown(content, "#FFD700")
    else:
        # Remove any stray asterisks
        cleaned = stripped.replace("*", "")
        colored_markdown(cleaned, "#FFD700")

# --- Display chat history (chatbox at the top, input in the middle) ---
for sender, message in st.session_state.messages:
    if sender == "Villain":
        colored_markdown(f"Villain: {message}", "#00FF00", bold=True)
    elif sender == "AI Sidekick":
        colored_markdown("AI Sidekick:", "#FF3333", bold=True)
        lines = message.split('\n')
        for line in lines:
            formatted_markdown(line)
    elif sender == "Image":
        st.image(message)

def send_message_callback():
    user_input = st.session_state["user_input"]
    if user_input.strip():
        send_message()
        st.session_state["user_input"] = ""

col1, col2 = st.columns([10, 1], gap="small")
with col1:
    user_input = st.text_area(
        "Message",
        placeholder="Type your message here...",
        key="user_input",
        label_visibility="collapsed",
        help="",
        on_change=send_message_callback
    )
with col2:
    send_clicked = st.button("➤", key="send_button")

if send_clicked:
    send_message()
    st.session_state["user_input"] = ""  # Clear the input before rerun
    st.rerun()  # <--- Use st.rerun() instead of st.experimental_rerun()

# --- Footer ---
st.markdown("<br><br><center><span style='color:#FFD700;'>Thank you for using the VillAin Chatbot!</span></center>", unsafe_allow_html=True)
