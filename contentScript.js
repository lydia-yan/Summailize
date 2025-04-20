// create sidebar DOM element - use independent namespace to avoid conflict with Gmail
function createSidebar() {
  // check if sidebar already exists, avoid duplicate creation
  if (document.getElementById('aimail-email-summary-sidebar')) {
    return document.getElementById('aimail-email-summary-sidebar');
  }

  const sidebarContainer = document.createElement('div');
  sidebarContainer.id = 'aimail-email-summary-sidebar'; // use unique prefix
  sidebarContainer.className = 'aimail-email-summary-sidebar'; // use unique prefix
  
  // add custom styles, avoid affecting Gmail styles
  const style = document.createElement('style');
  style.textContent = `
    .aimail-email-summary-sidebar {
      position: fixed;
      top: 60px;
      right: 0;
      width: 520px;
      height: calc(100vh - 60px);
      background: white;
      box-shadow: -2px 0 5px rgba(0,0,0,0.1);
      z-index: 9999;
      border-left: 1px solid #e0e0e0;
      display: none;
    }
    .aimail-email-summary-close-btn {
      position: absolute;
      top: 10px;
      right: 10px;
      width: 32px;
      height: 32px;
      background: transparent;
      border: none;
      font-size: 20px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #5f6368;
    }
    .aimail-email-summary-close-btn:hover {
      background-color: rgba(0, 0, 0, 0.05);
      border-radius: 50%;
    }
  `;
  document.head.appendChild(style);
  
  // add iframe to load React app
  const iframe = document.createElement('iframe');
  iframe.src = chrome.runtime.getURL('index.html');
  iframe.style.width = '100%';
  iframe.style.height = '100%';
  iframe.style.border = 'none';
  iframe.id = 'aimail-email-summary-iframe'; // use unique prefix
  sidebarContainer.appendChild(iframe);
  
  // add close button, use text instead of icon
  const closeButton = document.createElement('button');
  closeButton.className = 'aimail-email-summary-close-btn'; // use unique prefix
  closeButton.textContent = '✕';  // use text symbol instead of icon
  closeButton.addEventListener('click', toggleSidebar);
  sidebarContainer.appendChild(closeButton);
  
  sidebarContainer.style.display = 'none';
  
  document.body.appendChild(sidebarContainer);
  
  // wait for iframe to load and establish connection
  iframe.addEventListener('load', function() {
    setTimeout(() => {
      try {
        
        const currentEmailId = getCurrentEmailId();
        if (currentEmailId) {
          
          setTimeout(() => {
            notifyIframeAboutEmail(currentEmailId, iframe);
          }, 500);
        }
      } catch (error) {
        console.error('cannot connect to iframe:', error);
      }
    }, 500);
  });
  
  return sidebarContainer;
}

// toggle sidebar display status
function toggleSidebar() {
  const sidebar = document.getElementById('aimail-email-summary-sidebar');
  if (sidebar) {
    if (sidebar.style.display === 'none') {
      sidebar.style.display = 'block';
      
      // when sidebar is shown, force check current opened email and notify iframe
      const currentEmailId = getCurrentEmailId();
      if (currentEmailId) {
        const iframe = sidebar.querySelector('iframe');
        if (iframe && iframe.contentWindow) {
          
          window.__lastNotifiedEmailId = null;
          
          setTimeout(() => {
            notifyIframeAboutEmail(currentEmailId, iframe);
          }, 300);
        }
      }
    } else {
      sidebar.style.display = 'none';
    }
  }
}

let lastProcessedEmailId = null;

// simplified notification mechanism
function notifyIframeAboutEmail(emailId, iframe) {
  if (emailId === lastProcessedEmailId) {
    return;
  }
  
  lastProcessedEmailId = emailId;
  
  try {
    iframe.contentWindow.postMessage({
      type: 'CURRENT_EMAIL',
      emailId: emailId
    }, '*');
  } catch (error) {
    console.error('send message to iframe failed:', error);
  }
}

// use debounce to control URL detection frequency
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// record last processed URL and timestamp
let lastProcessedUrl = '';
let lastProcessTime = 0;

// URL change detection and message sending
function setupEmailDetection() {
  const processUrl = () => {
    const currentUrl = window.location.href;
    const now = Date.now();
    
    // if URL is not changed or the time interval is too short, return directly
    if (currentUrl === lastProcessedUrl || (now - lastProcessTime) < 1000) {
      return;
    }
    
    lastProcessedUrl = currentUrl;
    lastProcessTime = now;
    
    const emailId = getCurrentEmailId();
    if (!emailId) return;
    
    const sidebar = document.getElementById('aimail-email-summary-sidebar');
    if (!sidebar || sidebar.style.display === 'none') return;
    
    const iframe = sidebar.querySelector('iframe');
    if (!iframe || !iframe.contentWindow) return;
    
    // send message to iframe
    try {
      iframe.contentWindow.postMessage({
        type: 'CURRENT_EMAIL',
        emailId: emailId
      }, '*');
    } catch (error) {
      console.error('send message failed:', error);
    }
  };
  
  const debouncedProcessUrl = debounce(processUrl, 300);
  
  window.addEventListener('hashchange', debouncedProcessUrl);
  
}

// get current opened email ID
function getCurrentEmailId() {
  const match = window.location.hash.match(/#(?:inbox|all|sent|drafts|starred|snoozed|imp|trash|spam)\/([a-zA-Z0-9]+)/);
  return match ? match[1] : null;
}

// global variable, for tracking URL processing status
let isProcessingUrl = false;
let lastEmailIdFromUrl = null;

// listen to messages from background.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'toggleSummaryPanel') {
    toggleSidebar();
    sendResponse({ success: true });
    return true;
  }
  return false;
});

// remove GET_CURRENT_EMAIL message processing
('message', function(event) {
  const iframe = document.getElementById('aimail-email-summary-iframe');
  if (iframe && event.source === iframe.contentWindow) {

    return;
  }
});

// initialize extension
function init() {
  console.log('email summary assistant content script loaded');
  
  // ensure global variables are initialized correctly
  window.__lastNotifiedEmailId = null;
  isProcessingUrl = false;
  lastEmailIdFromUrl = null;
  isNotifying = false;
  isHandlingMessage = false;
  lastNotificationTime = 0;
  
  // avoid duplicate creation of sidebar and listeners
  if (window.__extensionInitialized) {
    return;
  }
  window.__extensionInitialized = true;
  
  // delay creating UI, avoid conflict with Gmail initialization
  setTimeout(() => {
    createSidebar();
    setupEmailDetection();
  }, 2000); 
}

if (!window.__extensionStarted) {
  window.__extensionStarted = true;
  setTimeout(init, 1500);
} 