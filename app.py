import streamlit as st
import requests
import re
import logging
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import google.generativeai as genai
from dotenv import load_dotenv
import os

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

def get_transcript(video_id: str):
    """Get transcript for a YouTube video"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript_list])
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        logger.error(f"Transcript error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error getting transcript: {str(e)}")
        return None

def generate_response(transcript: str, question: str):
    """Generate response using Gemini model"""
    try:
        prompt = f"""Based on the following YouTube video transcript, please answer the question. 
        If the answer cannot be found in the transcript, please say so.

        Transcript:
        {transcript}

        Question: {question}

        Answer:"""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return "Sorry, I encountered an error while generating the response."

def main():
    st.title("YTGPT")
    
    # Input YouTube URL
    video_url = st.text_input("Enter YouTube Video URL")
    
    if video_url:
        video_id = extract_video_id(video_url)
        if video_id:
            # Get video info
            video_info = get_video_info(video_id)
            if video_info:
                st.image(video_info["thumbnail_url"])
                st.subheader(video_info["title"])
                st.text(f"By: {video_info['author_name']}")
                
                # Get transcript
                transcript = get_transcript(video_id)
                if transcript:
                    # Chat interface
                    st.subheader("Ask questions about the video")
                    question = st.text_input("Your question")
                    
                    if question:
                        with st.spinner("Generating response..."):
                            response = generate_response(transcript, question)
                            st.write(response)
                else:
                    st.error("No transcript available for this video.")
            else:
                st.error("Could not fetch video information.")
        else:
            st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")

if __name__ == "__main__":
    main()