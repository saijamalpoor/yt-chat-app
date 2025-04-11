# YouTube Video Chat 

A web application that allows users to chat about YouTube videos using Google's Gemini AI.
![Demo](demo.gif)

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


