// initialize the React application
document.addEventListener('DOMContentLoaded', function() {
  console.log('email summary plugin loaded');
  
  // set up the message communication with the parent window
  window.addEventListener('message', function(event) {
    // handle the message from contentScript.js
    if (event.data && event.data.type === 'CURRENT_EMAIL') {
      console.log('received email ID:', event.data.emailId);
      // call the method of the React component to handle the email ID
    }
  });
}); 