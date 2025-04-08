// Function to create and inject the chat button
function injectChatButton() {
  const button = document.createElement('button');
  button.id = 'ytgpt-chat-button';
  button.innerHTML = 'Chat with Video';
  button.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 10px 20px;
    background-color: #FF4B4B;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    z-index: 1000;
    font-family: Arial, sans-serif;
    font-size: 14px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  `;

  button.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'openChat' });
  });

  document.body.appendChild(button);
}

// Check if we're on a YouTube video page
function isYouTubeVideoPage() {
  return window.location.hostname === 'www.youtube.com' && 
         window.location.pathname === '/watch' && 
         window.location.search.includes('v=');
}

// Initialize the extension
if (isYouTubeVideoPage()) {
  injectChatButton();
}

// Listen for URL changes (for YouTube's SPA navigation)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    if (isYouTubeVideoPage()) {
      injectChatButton();
    } else {
      const button = document.getElementById('ytgpt-chat-button');
      if (button) {
        button.remove();
      }
    }
  }
}).observe(document, { subtree: true, childList: true }); 