import streamlit as st
import requests
import re
import logging
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Page configuration
st.set_page_config(
    page_title="YTGPT - Chat with YouTube Videos",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stApp {
        background-color: #f5f5f5;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        width: 100px;
    }
    .stButton>button:hover {
        background-color: #FF3333;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        max-width: 85%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: auto;
        margin-right: 0;
        border-bottom-right-radius: 4px;
    }
    .assistant-message {
        background-color: white;
        margin-right: auto;
        margin-left: 0;
        border-bottom-left-radius: 4px;
    }
    .video-info {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .youtube-video {
        width: 100%;
        aspect-ratio: 16/9;
        margin-bottom: 1rem;
    }
    .chat-input {
        margin-top: 1rem;
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .message-text {
        margin: 0.5rem 0 0 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')

def extract_video_id(url):
    try:
        # Extract video ID from YouTube URL
        patterns = [
            r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})',
            r'(?:youtube\.com\/watch\?v=)([^"&?\/\s]{11})',
            r'(?:youtu\.be\/)([^"&?\/\s]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    except Exception as e:
        logger.error(f"Error extracting video ID: {str(e)}")
        return None

def get_video_info(video_id: str):
    """Get video info using YouTube's oembed API"""
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title", ""),
                "thumbnail_url": data.get("thumbnail_url", ""),
                "author_name": data.get("author_name", "")
            }
        return None
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        return None

def get_transcript(video_id):
    """
    Get transcript for a YouTube video with multiple fallback methods.
    """
    try:
        # Method 1: Try to get English transcript directly
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return transcript_list, None
    except TranscriptsDisabled:
        try:
            # Method 2: Try to get any available transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript_list, None
        except Exception as e:
            try:
                # Method 3: Try to get auto-generated transcript
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], auto_generated=True)
                return transcript_list, None
            except Exception as e:
                try:
                    # Method 4: Try to get transcript in any language and translate
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'hi'])
                    return transcript_list, None
                except Exception as e:
                    return None, f"Transcripts are disabled for this video. Error: {str(e)}"
    except NoTranscriptFound:
        try:
            # Method 5: Try to get auto-generated transcript in any language
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, auto_generated=True)
            return transcript_list, None
        except Exception as e:
            return None, f"No transcript found for this video. Error: {str(e)}"
    except Exception as e:
        return None, f"Error getting transcript: {str(e)}"

def generate_response(transcript_list, question: str):
    """
    Generate AI response based on transcript and question
    """
    try:
        # Convert transcript list to text
        transcript_text = " ".join([t["text"] for t in transcript_list])
        
        # Configure Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')
        
        # Create prompt
        prompt = f"""
        You are an AI assistant helping users understand YouTube videos. 
        Here is the video transcript:
        
        {transcript_text}
        
        Please answer this question about the video: {question}
        
        Provide a clear, concise, and accurate response based on the transcript.
        If the question cannot be answered from the transcript, say so.
        """
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return f"Sorry, I encountered an error while generating the response: {str(e)}"

def display_chat_messages():
    for message in st.session_state.chat_history:
        st.markdown(f"""
        <div class="chat-message {'user-message' if message['is_user'] else 'assistant-message'}">
            <strong>{'You' if message['is_user'] else 'Assistant'}:</strong>
            <p class="message-text">{message['text']}</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Sidebar
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/lib/streamlit/static/favicon.png", width=50)
        st.title("YTGPT")
        st.markdown("---")
        st.markdown("""
        ### How to use:
        1. Paste a YouTube video URL
        2. Wait for the video info to load
        3. Ask questions about the video
        
        ### Features:
        - 🌐 Multi-language support
        - 🤖 AI-powered responses
        - 📝 Transcript analysis
        """)
        st.markdown("---")
        st.markdown("Made with ❤️ using Streamlit")

    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎥 Enter YouTube Video URL")
        video_url = st.text_input("", placeholder="Paste YouTube URL here...")
        
        if video_url:
            video_id = extract_video_id(video_url)
            if video_id:
                # Get video info
                video_info = get_video_info(video_id)
                if video_info:
                    with st.container():
                        st.markdown(f"""
                        <div class="video-info">
                            <h3>{video_info["title"]}</h3>
                            <p>By: {video_info["author_name"]}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Embed YouTube video
                        st.markdown(f"""
                        <iframe class="youtube-video"
                            src="https://www.youtube.com/embed/{video_id}"
                            frameborder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowfullscreen>
                        </iframe>
                        """, unsafe_allow_html=True)
                        
                        # Get transcript
                        transcript_list, error_message = get_transcript(video_id)
                        if transcript_list:
                            st.markdown("### 💬 Chat about the video")
                            
                            # Display chat messages
                            display_chat_messages()
                            
                            # Input area
                            with st.container():
                                col1, col2 = st.columns([5,1])
                                with col1:
                                    question = st.text_input("", key="question_input", 
                                                        placeholder="What is this video about?")
                                with col2:
                                    send_button = st.button("Send", key="send_button", use_container_width=True)

                                if send_button and question:
                                    # Add user message to chat history
                                    st.session_state.chat_history.append({
                                        "text": question,
                                        "is_user": True
                                    })
                                    
                                    with st.spinner("🤔 Thinking..."):
                                        response = generate_response(transcript_list, question)
                                        
                                        # Add assistant response to chat history
                                        st.session_state.chat_history.append({
                                            "text": response,
                                            "is_user": False
                                        })
                                    
                                    # Clear input and rerun
                                    st.experimental_rerun()
                        else:
                            st.error(error_message or "No transcript available for this video.")
                else:
                    st.error("Could not fetch video information.")
            else:
                st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")
    
    with col2:
        if not video_url:
            st.markdown("""
            ### Welcome to YTGPT! 👋
            
            This AI-powered tool helps you interact with YouTube videos in a new way.
            Just paste a video URL and start asking questions about its content!
            
            #### Examples:
            - What are the main points discussed?
            - Can you summarize the video?
            - What was the conclusion?
            """)

if __name__ == "__main__":
    main()