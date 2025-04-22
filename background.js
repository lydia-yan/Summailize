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

// listen to messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getEmailData') {
    // check if this email ID has been processed, avoid duplicate requests
    if (processedEmails.has(request.emailId)) {
      console.log('email already processed, skip request:', request.emailId);
      sendResponse({ 
        success: true, 
        data: { 
          url: `https://mail.google.com/mail/u/0/#inbox/${request.emailId}`,
          id: request.emailId,
          cached: true 
        } 
      });
      return true;
    }
    
    // only process email URL, not content
    const emailUrl = `https://mail.google.com/mail/u/0/#inbox/${request.emailId}`;
    
    processedEmails.add(request.emailId);
    
    if (processedEmails.size > 100) {
      // remove the oldest element (convert to array and take first 20)
      const toRemove = Array.from(processedEmails).slice(0, 20);
      toRemove.forEach(id => processedEmails.delete(id));
    }
    
    // use setTimeout to delay sending request, avoid blocking main thread
    setTimeout(() => {
      sendToBackend(emailUrl, request.emailId)
        .then(result => {
        })
        .catch(error => {
          console.error('send to backend failed:', error);
        });
    }, 500);
    
    // immediately respond to content script, not waiting for backend request to complete
    sendResponse({ 
      success: true, 
      data: { 
        url: emailUrl, 
        id: request.emailId 
      } 
    });
    
    return true;
  }
  
  return false;
});

// send data to backend function
async function sendToBackend(emailUrl, emailId) {
  try {
    // replace with your backend API address
    const backendUrl = 'https://your-backend-api/process-email';
    
    console.log('send email URL to backend:', emailUrl);
    
    //change to a real API request
    /*
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        emailUrl: emailUrl,
        emailId: emailId
      }),
    });
    
    if (!response.ok) {
      throw new Error('backend request failed: ' + response.status);
    }
    
    return await response.json();
    */
    
    // simulate success response
    return { success: true };
  } catch (error) {
    console.error('send to backend failed:', error);
    throw error;
  }
} 