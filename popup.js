document.addEventListener('DOMContentLoaded', function() {
  const chatContainer = document.getElementById('chatContainer');
  const userInput = document.getElementById('userInput');
  const sendButton = document.getElementById('sendButton');

  // Function to add a message to the chat
  function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
    messageDiv.textContent = message;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // Function to get the current YouTube video ID
  async function getCurrentVideoId() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = new URL(tab.url);
    return url.searchParams.get('v');
  }

  // Function to send message to the backend
  async function sendMessage(message) {
    const videoId = await getCurrentVideoId();
    if (!videoId) {
      addMessage("Please navigate to a YouTube video first.");
      return;
    }

    try {
      const response = await fetch('YOUR_STREAMLIT_APP_URL/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_id: videoId,
          message: message
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        addMessage(data.response);
      } else {
        addMessage("Sorry, I encountered an error while processing your request.");
      }
    } catch (error) {
      console.error('Error:', error);
      addMessage("Sorry, I encountered an error while processing your request.");
    }
  }

  // Event listener for the send button
  sendButton.addEventListener('click', async () => {
    const message = userInput.value.trim();
    if (message) {
      addMessage(message, true);
      userInput.value = '';
      await sendMessage(message);
    }
  });

  // Event listener for Enter key
  userInput.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
      const message = userInput.value.trim();
      if (message) {
        addMessage(message, true);
        userInput.value = '';
        await sendMessage(message);
      }
    }
  });
}); 