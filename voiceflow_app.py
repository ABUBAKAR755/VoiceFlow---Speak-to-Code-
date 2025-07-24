import streamlit as st
import os
from datetime import datetime
import tempfile
import io
import base64

# Optional imports with error handling
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    st.error(
        "Google Generative AI package not installed. Please run: pip install google-generativeai")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# Configure page
st.set_page_config(
    page_title="🎙️ VoiceFlow - Speak to Code",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'mood_logs' not in st.session_state:
    st.session_state.mood_logs = []
if 'is_listening' not in st.session_state:
    st.session_state.is_listening = False

# Function to process user input - MOVED TO TOP


def process_user_input(user_input, api_key, model, api_choice, enable_tts, tts_speed):
    if not api_key:
        st.error(f"AIzaSyAgXo1hojVLo3ra-MWQam3bxsjLqdplEPo")
        return

    # Check if required package is available
    if api_choice == "Google Gemini (Recommended)" and not GEMINI_AVAILABLE:
        st.error(
            "Google Generative AI package not installed! Please run: pip install google-generativeai")
        return
    elif api_choice == "OpenAI GPT" and not OPENAI_AVAILABLE:
        st.error("OpenAI package not installed! Please run: pip install openai")
        return

    with st.spinner("🤖 VoiceFlow is thinking..."):
        try:
            system_prompt = """You are VoiceFlow, a multilingual AI coding assistant. 
            You help users with:
            - Writing code in any programming language
            - Explaining code concepts clearly
            - Debugging and fixing code issues
            - Converting code between languages
            - Teaching programming concepts
            
            Always provide:
            1. Clear, working code when requested
            2. Step-by-step explanations
            3. Best practices and tips
            4. Error handling when relevant
            
            Format your responses with proper code blocks and clear explanations."""

            if api_choice == "Google Gemini (Recommended)":
                # Configure Gemini
                genai.configure(api_key=api_key)
                model_instance = genai.GenerativeModel(model)

                # Create full prompt for Gemini
                full_prompt = f"{system_prompt}\n\nUser Request: {user_input}"

                # Generate response
                response = model_instance.generate_content(full_prompt)
                ai_response = response.text

            else:  # OpenAI GPT
                # Create OpenAI client (updated for newer versions)
                if hasattr(openai, 'OpenAI'):
                    # For openai >= 1.0.0
                    client = openai.OpenAI(api_key=api_key)

                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input}
                        ],
                        max_tokens=1500,
                        temperature=0.7
                    )

                    ai_response = response.choices[0].message.content

                else:
                    # For older openai versions
                    openai.api_key = api_key

                    response = openai.ChatCompletion.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input}
                        ],
                        max_tokens=1500,
                        temperature=0.7
                    )

                    ai_response = response.choices[0].message.content

            # Add to chat history
            st.session_state.chat_history.append({
                'user': user_input,
                'ai': ai_response,
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'api_used': api_choice
            })

            # Text-to-Speech
            if enable_tts and TTS_AVAILABLE:
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', int(tts_speed * 200))
                    engine.say("Response generated successfully!")
                    engine.runAndWait()
                except:
                    st.info("🔊 TTS attempted but may not work in web environment")
            elif enable_tts:
                st.success(
                    "🔊 Text-to-Speech enabled! (Install pyttsx3 for actual speech)")

            # Rerun to update chat display
            st.rerun()

        except Exception as e:
            st.error(f"Error with {api_choice}: {str(e)}")
            if "api_key" in str(e).lower() or "invalid" in str(e).lower():
                st.info(
                    f"Make sure your {api_choice} API key is valid and you have sufficient credits.")
            elif "quota" in str(e).lower():
                st.info("You may have exceeded your API quota. Check your account.")
            else:
                st.info("Check your internet connection and API key.")


# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    .ai-message {
        background-color: #f3e5f5;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #9c27b0;
    }
    .mood-selector {
        font-size: 2rem;
        text-align: center;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎙️ VoiceFlow - Speak to Code 🚀</h1>
    <p>Multilingual AI Coding Assistant | Voice → Code → Learn</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Selection
    api_choice = st.selectbox("Choose AI Service",
                              ["Google Gemini (Recommended)", "OpenAI GPT"],
                              index=0)

    # API Key Input
    if api_choice == "Google Gemini (Recommended)":
        api_key = st.text_input("Google Gemini API Key", type="password",
                                help="Get your free API key from https://makersuite.google.com/app/apikey")
        if not GEMINI_AVAILABLE:
            st.error("Please install: pip install google-generativeai")
    else:
        api_key = st.text_input("OpenAI API Key", type="password",
                                help="Enter your OpenAI API key")
        if not OPENAI_AVAILABLE:
            st.error("Please install: pip install openai")

    # Model Selection
    if api_choice == "Google Gemini (Recommended)":
        model_choice = st.selectbox("Gemini Model",
                                    ["gemini-1.5-flash",
                                        "gemini-1.5-pro", "gemini-pro"],
                                    index=0,
                                    help="Flash is fastest, Pro is most capable")
    else:
        model_choice = st.selectbox("OpenAI Model",
                                    ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                                    index=0)

    # Language Settings
    st.subheader("🌍 Language Settings")
    input_language = st.selectbox("Input Language",
                                  ["Auto-detect", "English", "Spanish", "French",
                                   "German", "Hindi", "Urdu", "Chinese", "Japanese"])

    # Voice Settings
    st.subheader("🔊 Voice Settings")
    if TTS_AVAILABLE:
        enable_tts = st.checkbox("Enable Text-to-Speech", value=True)
        tts_speed = st.slider("Speech Speed", 0.5, 2.0, 1.0, 0.1)
    else:
        st.info("TTS not available. Install pyttsx3: pip install pyttsx3")
        enable_tts = False
        tts_speed = 1.0

    # Mood Tracker
    st.subheader("😊 Mood Tracker")
    mood_options = ["😊 Happy", "😐 Neutral", "😞 Sad",
                    "😡 Frustrated", "🤔 Confused", "🎉 Excited"]
    current_mood = st.selectbox("Current Mood", mood_options)

    if st.button("Log Mood"):
        st.session_state.mood_logs.append({
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'mood': current_mood
        })
        st.success("Mood logged!")

    # Session Stats
    st.subheader("📊 Session Stats")
    st.metric("Total Queries", len(st.session_state.chat_history))
    st.metric("Mood Logs", len(st.session_state.mood_logs))

# Main Application
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Voice & Text Interface")

    # Voice Input Section
    st.subheader("🎙️ Voice Input")

    if SPEECH_RECOGNITION_AVAILABLE:
        st.info("🎤 Speech recognition available!")
        # Real voice input would go here
        voice_input = st.text_area("🎤 Voice input (speak and it will be transcribed):",
                                   placeholder="Example: Create a Python function to reverse a string",
                                   height=100)
    else:
        st.warning(
            "Speech recognition not available. Install with: pip install SpeechRecognition")
        voice_input = st.text_area("🎤 Text input (simulated voice input):",
                                   placeholder="Example: Create a Python function to reverse a string",
                                   height=100)

    # Alternative: File upload for voice
    uploaded_audio = st.file_uploader(
        "Or upload audio file", type=['wav', 'mp3', 'm4a'])

    col_voice1, col_voice2 = st.columns(2)
    with col_voice1:
        if st.button("🎙️ Start Listening (Simulated)", type="primary"):
            st.info(
                "🎤 Listening... (In real implementation, this would use speech recognition)")

    with col_voice2:
        if st.button("💬 Process Voice Input"):
            if voice_input.strip():
                process_user_input(
                    voice_input, api_key, model_choice, api_choice, enable_tts, tts_speed)

    # Text Input Alternative
    st.subheader("⌨️ Text Input (Alternative)")
    text_input = st.text_input("Type your coding request:")
    if st.button("📝 Process Text Input"):
        if text_input.strip():
            process_user_input(text_input, api_key, model_choice,
                               api_choice, enable_tts, tts_speed)

    # Chat History
    st.subheader("💭 Chat History")
    chat_container = st.container()

    with chat_container:
        for i, chat in enumerate(st.session_state.chat_history):
            st.markdown(f"""
            <div class="user-message">
                <strong>🧑‍💻 You:</strong> {chat['user']}
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="ai-message">
                <strong>🤖 VoiceFlow ({chat.get('api_used', 'AI')}):</strong><br>
                {chat['ai']}
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.header("🎯 Quick Actions")

    # Predefined coding tasks
    st.subheader("🚀 Quick Coding Tasks")
    quick_tasks = [
        "Create a Python class for a bank account",
        "Write a function to sort a list of dictionaries",
        "Explain how recursion works with examples",
        "Debug this code: print('Hello World'",
        "Convert this Python code to JavaScript",
        "Create a REST API endpoint in Flask",
        "Write a SQL query to find duplicate records",
        "Explain machine learning in simple terms"
    ]

    for task in quick_tasks:
        if st.button(task, key=f"quick_{task[:20]}"):
            process_user_input(task, api_key, model_choice,
                               api_choice, enable_tts, tts_speed)

    # File Upload Section
    st.subheader("📁 File Operations")
    uploaded_code = st.file_uploader("Upload code file for analysis",
                                     type=['py', 'js', 'java', 'cpp', 'html', 'css'])

    if uploaded_code:
        file_content = uploaded_code.read().decode('utf-8')
        st.code(file_content, language='python')

        if st.button("🔍 Analyze This Code"):
            analysis_prompt = f"Analyze and explain this code:\n\n```\n{file_content}\n```"
            process_user_input(analysis_prompt, api_key,
                               model_choice, api_choice, enable_tts, tts_speed)

    # Mood History
    if st.session_state.mood_logs:
        st.subheader("📈 Mood Timeline")
        for log in st.session_state.mood_logs[-5:]:  # Show last 5 moods
            st.write(f"{log['timestamp']}: {log['mood']}")

# Function to process user input


def process_user_input(user_input, api_key, model, enable_tts, tts_speed):
    if not OPENAI_AVAILABLE:
        st.error("OpenAI package not installed! Please run: pip install openai")
        return

    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar!")
        return

    with st.spinner("🤖 VoiceFlow is thinking..."):
        try:
            # Create OpenAI client (updated for newer versions)
            if hasattr(openai, 'OpenAI'):
                # For openai >= 1.0.0
                client = openai.OpenAI(api_key=api_key)

                system_prompt = """You are VoiceFlow, a multilingual AI coding assistant. 
                You help users with:
                - Writing code in any programming language
                - Explaining code concepts clearly
                - Debugging and fixing code issues
                - Converting code between languages
                - Teaching programming concepts
                
                Always provide:
                1. Clear, working code when requested
                2. Step-by-step explanations
                3. Best practices and tips
                4. Error handling when relevant
                
                Format your responses with proper code blocks and clear explanations."""

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=1500,
                    temperature=0.7
                )

                ai_response = response.choices[0].message.content

            else:
                # For older openai versions
                openai.api_key = api_key

                system_prompt = """You are VoiceFlow, a multilingual AI coding assistant. 
                You help users with:
                - Writing code in any programming language
                - Explaining code concepts clearly
                - Debugging and fixing code issues
                - Converting code between languages
                - Teaching programming concepts
                
                Always provide:
                1. Clear, working code when requested
                2. Step-by-step explanations
                3. Best practices and tips
                4. Error handling when relevant
                
                Format your responses with proper code blocks and clear explanations."""

                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=1500,
                    temperature=0.7
                )

                ai_response = response.choices[0].message.content

            # Add to chat history
            st.session_state.chat_history.append({
                'user': user_input,
                'ai': ai_response,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })

            # Text-to-Speech
            if enable_tts and TTS_AVAILABLE:
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', int(tts_speed * 200))
                    engine.say("Response generated successfully!")
                    engine.runAndWait()
                except:
                    st.info("🔊 TTS attempted but may not work in web environment")
            elif enable_tts:
                st.success(
                    "🔊 Text-to-Speech enabled! (Install pyttsx3 for actual speech)")

            # Rerun to update chat display
            st.rerun()

        except Exception as e:
            st.error(f"Error: {str(e)}")
            if "api_key" in str(e).lower():
                st.info(
                    "Make sure your OpenAI API key is valid and you have sufficient credits.")
            else:
                st.info("Check your internet connection and API key.")


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <h3>🚀 VoiceFlow Features</h3>
    <p>✨ Multilingual Support | 🎙️ Voice Interface | 🤖 AI-Powered | 📊 Mood Tracking | 🔊 Text-to-Speech</p>
    <p>Built for Hackathons | Perfect for Learning | Accessibility-First</p>
</div>
""", unsafe_allow_html=True)

# Instructions for users
with st.expander("📖 How to Use VoiceFlow"):
    st.markdown("""
    ### 🎯 Getting Started:
    1. **Add OpenAI API Key**: Enter your API key in the sidebar
    2. **Choose Input Method**: Use voice simulation or text input
    3. **Ask Coding Questions**: Request code, explanations, or debugging help
    4. **Track Your Mood**: Log how you feel while coding
    5. **Upload Files**: Analyze existing code files
    
    ### 🎙️ Voice Commands Examples:
    - "Create a Python function to calculate fibonacci numbers"
    - "Explain how machine learning works in simple terms"
    - "Debug this JavaScript code for me"
    - "Convert this Python code to Java"
    - "Write a SQL query to find all users older than 25"
    
    ### 🌟 Pro Tips:
    - Be specific in your requests for better results
    - Use the quick action buttons for common tasks
    - Track your mood to see coding productivity patterns
    - Upload files for instant code analysis
    """)

# Development Notes
with st.expander("🛠️ Implementation Notes"):
    st.markdown("""
    ### 🚀 Current Implementation:
    - ✅ Streamlit-based UI with voice simulation
    - ✅ OpenAI GPT integration for code generation
    - ✅ Chat history and mood tracking
    - ✅ File upload and analysis
    - ✅ Multi-language support ready
    
    ### 🎯 For Full Implementation:
    - 🔧 Replace simulated voice with `speech_recognition` library
    - 🔧 Add real-time audio recording with `streamlit-webrtc`
    - 🔧 Implement actual TTS with `pyttsx3` or Google TTS
    - 🔧 Add language detection with `langdetect`
    - 🔧 Deploy on Streamlit Cloud or Heroku
    
    ### 📦 Required Packages:
    ```bash
    # For Google Gemini (Recommended):
    pip install streamlit google-generativeai
    
    # For OpenAI (Alternative):
    pip install streamlit openai
    
    # Full installation (optional features):
    pip install streamlit google-generativeai SpeechRecognition pyttsx3
    ```
    
    ### 🎯 Package Status:
    - ✅ Streamlit: Available
    - {f"✅" if GEMINI_AVAILABLE else "❌"} Google Generative AI: {f"Available" if GEMINI_AVAILABLE else "Not installed"}
    - {f"✅" if OPENAI_AVAILABLE else "❌"} OpenAI: {f"Available" if OPENAI_AVAILABLE else "Not installed"}
    - {f"✅" if SPEECH_RECOGNITION_AVAILABLE else "❌"} SpeechRecognition: {f"Available" if SPEECH_RECOGNITION_AVAILABLE else "Not installed"}  
    - {f"✅" if TTS_AVAILABLE else "❌"} pyttsx3: {f"Available" if TTS_AVAILABLE else "Not installed"}
    
    ### 🔑 Getting API Keys:
    - **Google Gemini (FREE)**: https://makersuite.google.com/app/apikey
    - **OpenAI**: https://platform.openai.com/api-keys
    """)
