import streamlit as st
import requests
import re
import logging

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

# Backend API URL
API_URL = "http://localhost:8000"

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

def main():
    st.title("YTGPT")
    
    # Debug section
    if st.sidebar.checkbox("Show Debug Info"):
        st.sidebar.subheader("Debug Information")
        st.sidebar.text("Logs will appear here")
    
    # Input YouTube URL
    video_url = st.text_input("Enter YouTube Video URL")
    
    if video_url:
        video_id = extract_video_id(video_url)
        if video_id:
            st.info(f"Video ID: {video_id}")
            
            try:
                # Get video information
                response = requests.get(f"{API_URL}/video-info/{video_id}")
                
                if response.status_code == 200:
                    video_info = response.json()
                    
                    if video_info.get("status") == "success":
                        # Display video
                        st.video(video_url)
                        
                        # Display video title
                        st.subheader(video_info["title"])
                        
                        # Chat interface
                        st.subheader("Chat about the video")
                        user_message = st.text_input("Your message")
                        
                        if user_message:
                            try:
                                chat_response = requests.post(
                                    f"{API_URL}/chat",
                                    json={
                                        "video_id": video_id,
                                        "message": user_message
                                    },
                                    headers={"Content-Type": "application/json"}
                                )
                                
                                if chat_response.status_code == 200:
                                    response_data = chat_response.json()
                                    if response_data.get("status") == "success":
                                        st.write("Assistant:", response_data["response"])
                                    else:
                                        st.error("Error in chat response")
                                else:
                                    error_detail = chat_response.json().get("detail", "Unknown error")
                                    st.error(f"Error in chat response: {error_detail}")
                                    logger.error(f"Chat error: {error_detail}")
                            except requests.exceptions.RequestException as e:
                                st.error(f"Network error during chat: {str(e)}")
                                logger.error(f"Network error during chat: {str(e)}")
                            except Exception as e:
                                st.error(f"Unexpected error during chat: {str(e)}")
                                logger.error(f"Unexpected error during chat: {str(e)}")
                    else:
                        st.error("Error in video information response")
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"Error fetching video information: {error_detail}")
                    logger.error(f"Backend error: {error_detail}")
            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {str(e)}")
                logger.error(f"Network error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                logger.error(f"Unexpected error: {str(e)}")
        else:
            st.error("Invalid YouTube URL. Please enter a valid YouTube URL.")

if __name__ == "__main__":
    main()