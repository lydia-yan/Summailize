// listen to extension installation event
chrome.runtime.onInstalled.addListener(() => {
  console.log('email summary assistant installed');
  
  // get the user email and save to storage
  chrome.identity.getProfileUserInfo({ accountStatus: 'ANY' }, (userInfo) => {
    if (userInfo.email) {
      // save the user email to storage
      chrome.storage.local.set({ userEmail: userInfo.email }, () => {
        console.log('user email is saved:', userInfo.email);
      });
    } else {
      console.log('failed to get the user email or the user is not logged in Google account');
    }
  });
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

// handle the request from the content script to get the user email
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getUserEmail') {
    chrome.storage.local.get(['userEmail'], (result) => {
      if (result.userEmail) {
        sendResponse({ email: result.userEmail });
      } else {
        // if no cached email, try to get it again
        chrome.identity.getProfileUserInfo({ accountStatus: 'ANY' }, (userInfo) => {
          if (userInfo.email) {
            chrome.storage.local.set({ userEmail: userInfo.email });
            sendResponse({ email: userInfo.email });
          } else {
            sendResponse({ email: null });
          }
        });
        return true; // keep the message channel open, allow asynchronous response
      }
    });
    return true; // asynchronous response needs to return true
  }
});
