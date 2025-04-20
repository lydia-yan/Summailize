// the background script of the extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('AIMAIL Gmail Summary Assistant installed');
  
  // Initialize default settings
  chrome.storage.sync.set({
    summaryEnabled: true,
    timeRange: '7days',
    language: 'en',
    apiKey: '',
    apiEndpoint: 'https://backend-api/summarize'
  });
});

// listen to the messages from the content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getSummary') {
    // get the API key and endpoint
    chrome.storage.sync.get(['apiKey', 'apiEndpoint'], (data) => {
      const { apiKey, apiEndpoint } = data;
      
      // send the summary request to the API
      fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          emailContent: request.emailContent,
          emailUrl: request.emailUrl,
          timeRange: request.timeRange
        })
      })
      .then(response => response.json())
      .then(summaryData => {
        sendResponse({ success: true, summary: summaryData });
      })
      .catch(error => {
        console.error('获取摘要时出错:', error);
        sendResponse({ success: false, error: error.message });
      });
    });
    
    // return true to indicate that the response will be sent asynchronously
    return true;
  }
  
  if (request.action === 'openSettings') {
    chrome.runtime.openOptionsPage();
    sendResponse({ success: true });
  }
});

// add the icon click event
chrome.action.onClicked.addListener((tab) => {
  // only activate on Gmail page
  if (tab.url && tab.url.includes('mail.google.com')) {
    chrome.tabs.sendMessage(tab.id, { action: 'toggleSummaryPanel' });
  } else {
    // if not on Gmail page, open Gmail
    chrome.tabs.create({ url: 'https://mail.google.com' });
  }
}); 