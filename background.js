// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'openChat') {
    // Open the popup
    chrome.windows.create({
      url: 'popup.html',
      type: 'popup',
      width: 400,
      height: 500
    });
  }
}); 