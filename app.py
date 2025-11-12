# app.py
import streamlit as st
import os
import base64
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# --- Configuration and Setup ---
st.set_page_config(
    page_title="Manara - Your Guide to ATS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
CUSTOM_CSS = """
/* Modern Dark Theme */
:root {
    --primary: #74c69d;
    --secondary: #2d6a4f;
    --dark-bg: #0d1b2a;
    --card-bg: #152238;
    --accent: #40916c;
}
body {
    background: linear-gradient(135deg, var(--dark-bg) 0%, #1b3a4b 100%);
    margin:0;
    padding:0;
    font-family:'Segoe UI',system-ui,sans-serif;
}
.stApp {
    background: linear-gradient(135deg, var(--dark-bg) 0%, #1b3a4b 100%);
}
.header {
    background: linear-gradient(135deg, var(--secondary) 0%, var(--accent) 100%);
    padding: 1.5rem 2rem;
    border-radius: 0 0 20px 20px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,.3);
    position: relative;
}
.lang-badge {
    background: rgba(255,255,255,0.15);
    padding: 6px 16px;
    border-radius: 30px;
    font-size: 0.85em;
    font-weight: 600;
    color: white;
    backdrop-filter: blur(5px);
    border: 1px solid rgba(116,198,157,0.4);
    animation: pulse-glow 2s infinite ease-in-out;
    display: inline-block;
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 5px rgba(116,198,157,0.4); transform: scale(1); }
    50% { box-shadow: 0 0 15px rgba(116,198,157,0.8); transform: scale(1.05); }
}
.section-card {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
    border: 1px solid rgba(116,198,157,.2);
    box-shadow: 0 4px 20px rgba(0,0,0,.1);
}
[data-testid="stHeader"] {
    display: none;
}
.st-emotion-cache-18ni2g1 {
    padding-top: 0;
}
.st-emotion-cache-1wa0z9t {
    background-color: transparent;
}
.st-emotion-cache-10trblm {
    color: var(--primary);
}
.stChatMessage {
    color: #ffffff !important;
}
.st-emotion-cache-4oy32v {
    background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
    color: white !important;
}
.st-emotion-cache-1r4qj8x {
    background: rgba(255,255,255,.1) !important;
    color: #e9f5ee !important;
    border: 1px solid rgba(255,255,255,.1);
}
"""

st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# --- Helper Functions ---

def get_logo_base64():
    """Get logo as base64."""
    try:
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return None

def get_ats_logo_base64():
    """Get ATS logo as base64."""
    try:
        # Try different possible locations
        base_dir = os.path.dirname(__file__)
        possible_paths = [
            os.path.join(base_dir, "atslogo.jpg"),
            os.path.join(base_dir, "atslogo.png"),
            "atslogo.jpg",
            "atslogo.png"
        ]
        
        for logo_path in possible_paths:
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
                    
    except Exception:
        pass
    return None

def initialize_rag():
    """Initialize RAG system."""
    try:
        from rag_chat import answer
        return answer
    except Exception as e:
        st.error(f"Error initializing RAG system: {str(e)}")
        return None

# --- UI Components ---

def header_html():
    """Generates the custom header HTML."""
    logo_base64 = get_logo_base64()
    ats_logo_base64 = get_ats_logo_base64()

    logo_html = f'''
        <img src="data:image/png;base64,{logo_base64}" alt="Manara Logo"
             style="height:130px; width:auto; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.3);">
    ''' if logo_base64 else "🧠"

    ats_html = f'''
        <img src="data:image/jpeg;base64,{ats_logo_base64}" alt="ATS Logo"
             style="height:130px; width:auto; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.3);">
    ''' if ats_logo_base64 else "🏫"

    html = f"""
    <div class="header" style="display:flex; align-items:center; justify-content:space-between; position:relative;">
        <div style="margin-left:2rem;">{logo_html}</div>
        <div style="text-align:center;">
            <h1 style="color:white; margin:0; font-size:3.5em; font-weight:700; letter-spacing:2px;">Manara</h1>
            <p style="color:rgba(255,255,255,.9); font-size:1.2em; margin:8px 0 0 0;">Your Guide to ATS</p>
            <div style="display:flex; justify-content:center; gap:12px; margin-top:12px;">
                <span class="lang-badge">العربية</span>
                <span class="lang-badge">English</span>
            </div>
        </div>
        <div style="margin-right:2rem;">{ats_html}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def features_html():
    """Generates the features section HTML."""
    html = """
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin:20px 0;">
        <div class="section-card"><h4 style="color:#74c69d;margin:0 0 10px 0;">Admissions</h4><p style="color:#d8f3dc;margin:0;font-size:.9em;">Requirements, deadlines, procedures</p></div>
        <div class="section-card"><h4 style="color:#74c69d;margin:0 0 10px 0;">Fees & Costs</h4><p style="color:#d8f3dc;margin:0;font-size:.9em;">Tuition, scholarships, payment</p></div>
        <div class="section-card"><h4 style="color:#74c69d;margin:0 0 10px 0;">Curriculum</h4><p style="color:#d8f3dc;margin:0;font-size:.9em;">Programs, courses, schedules</p></div>
        <div class="section-card"><h4 style="color:#74c69d;margin:0 0 10px 0;">Locations</h4><p style="color:#d8f3dc;margin:0;font-size:.9em;">Campuses, facilities, contacts</p></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Main Application Logic ---

def main():
    # Initialize RAG function
    rag_answer = initialize_rag()
    
    if not rag_answer:
        st.error("Chatbot functionality is currently unavailable. Please check the configuration.")
        return

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "quick_action_triggered" not in st.session_state:
        st.session_state.quick_action_triggered = None

    # 1. Header and Features
    header_html()
    features_html()
    
    # 2. Clear Chat Button
    col_clear = st.columns([3, 1])[1]
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat_btn"):
            st.session_state.messages = []
            st.session_state.quick_action_triggered = None
            st.rerun()

    # 3. Layout for Chat and Sidebar
    col1, col2 = st.columns([3, 1])

    with col1:
        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle quick action triggered questions
        if st.session_state.quick_action_triggered:
            prompt = st.session_state.quick_action_triggered
            st.session_state.quick_action_triggered = None
            
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get bot response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                
                try:
                    response = rag_answer(prompt, st.session_state.messages)
                    message_placeholder.markdown(response)
                except Exception as e:
                    error_msg = f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"
                    message_placeholder.markdown(error_msg)
                    response = error_msg
            
            # Add bot response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Rerun to show the new messages
            st.rerun()

        # Regular chat input
        if prompt := st.chat_input("Ask a question about ATS...", key="chat_input"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get bot response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                
                try:
                    greeting_keywords = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings", "howdy"]
                    is_greeting = any(keyword in prompt.lower() for keyword in greeting_keywords) and len(prompt.split()) <= 3
                    
                    if is_greeting:
                        response = "Hello, my name is Manara. I'm a friendly bilingual assistant for Applied Technology Schools (ATS) in UAE. I'm here to help with any questions you may have about ATS. How can I assist you today?"
                    else:
                        response = rag_answer(prompt, st.session_state.messages)
                    
                    message_placeholder.markdown(response)
                    
                except Exception as e:
                    error_msg = f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"
                    message_placeholder.markdown(error_msg)
                    response = error_msg
            
            # Add bot response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

    with col2:
        # Quick Actions Group
        st.markdown("""
        <div class="section-card">
            <h3 style="color:#74c69d;margin-top:0;">Quick Actions</h3>
            <p style="color:#d8f3dc;font-size:.9em;margin-bottom:15px;">Click to ask common questions:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick action buttons - these will AUTO-SUBMIT immediately
        if st.button("Admission Info", key="quick_action_1", use_container_width=True):
            st.session_state.quick_action_triggered = "What are the admission requirements?"
            st.rerun()
            
        if st.button("Fee Structure", key="quick_action_2", use_container_width=True):
            st.session_state.quick_action_triggered = "How much are the tuition fees?"
            st.rerun()
            
        if st.button("Programs", key="quick_action_3", use_container_width=True):
            st.session_state.quick_action_triggered = "What programs are available at ATS?"
            st.rerun()
            
        if st.button("Locations", key="quick_action_4", use_container_width=True):
            st.session_state.quick_action_triggered = "Where are the ATS campuses located?"
            st.rerun()

        # About ATS Group
        st.markdown("""
        <div class="section-card">
            <h3 style="color:#74c69d;margin-top:0;">About ATS</h3>
            <p style="color:#d8f3dc;font-size:.9em;line-height:1.4;">
                Applied Technology Schools provide vocational and technical education in the UAE,
                offering industry-relevant programs and career-focused training.
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()