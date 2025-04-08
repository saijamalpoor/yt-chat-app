# YouTube Video Chat 

A web application that allows users to chat about YouTube videos using Google's Gemini AI.

## Features

- YouTube video embedding
- Video transcript extraction
- AI-powered chat about video content


## Setup

1. Clone the repository:
```bash
git clone https://github.com/saijamalpoor/yt-chat-app.git
cd youtube-chat-app
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Gemini API key:


5. Start the backend server:
```bash
uvicorn main:app --reload
```

6. In a new terminal, start the frontend:
```bash
streamlit run app.py
```

## Project Structure

```text
youtube-chat-app
├── .env # Environment variables
├── .gitignore # Git ignore file
├── README.md # Project documentation
├── requirements.txt # Python dependencies
├── main.py # Backend FastAPI server
└── app.py # Frontend Streamlit app
```

## Dependencies

- FastAPI
- Streamlit
- Google Generative AI
- YouTube Transcript API
- PyTube
- Python-dotenv

## License

MIT

# YTGPT Chrome Extension

A Chrome extension that allows you to chat with YouTube videos using AI.

## Features

- Chat with any YouTube video using AI
- Get instant answers about video content
- Clean and intuitive interface
- Works with any YouTube video that has captions

## Installation

1. Clone this repository
2. Open Chrome and go to `chrome://extensions/`
3. Enable "Developer mode" in the top right corner
4. Click "Load unpacked" and select the extension directory
5. The extension should now be installed and ready to use

## Usage

1. Navigate to any YouTube video
2. Click the "Chat with Video" button that appears in the bottom right corner
3. Ask questions about the video in the chat interface
4. Get AI-powered responses based on the video's content

## Development

To modify the extension:

1. Make changes to the source files
2. Go to `chrome://extensions/`
3. Find the YTGPT extension and click the refresh icon
4. The changes will be applied

## Files Structure

- `manifest.json` - Extension configuration
- `popup.html` - Chat interface
- `popup.js` - Chat functionality
- `content.js` - YouTube page integration
- `background.js` - Extension background processes
- `icons/` - Extension icons

## Requirements

- Chrome browser
- YouTube video with captions
- Internet connection

## Note

Make sure to replace `YOUR_STREAMLIT_APP_URL` in `popup.js` with your actual Streamlit app URL before using the extension.

