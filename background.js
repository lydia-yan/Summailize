// listen to extension installation event
chrome.runtime.onInstalled.addListener(() => {
  console.log('email summary assistant installed');
});

const processedEmails = new Set();

// listen to extension icon click event
chrome.action.onClicked.addListener((tab) => {
  if (tab.url.includes('mail.google.com')) {
    chrome.tabs.sendMessage(tab.id, { action: 'toggleSummaryPanel' })
      .catch(error => {
        console.error('send message failed:', error);
      });
  } else {
    chrome.tabs.create({ url: 'https://mail.google.com' });
  }
});
