// allow communication with parent window
window.addEventListener('message', function(event) {
    // check the message source
    if (event.origin.includes('mail.google.com') || event.origin === window.location.origin) {
        console.log('iframe received message:', event.data);
        
        // set the flag to indicate the connection is established
        if (event.data.type === 'CONNECT') {
            console.log('establish connection with parent window');
            // send the confirmation message to the parent window
            if (window.parent && window.parent !== window) {
                window.parent.postMessage({ type: 'CONNECTED' }, '*');
            }
        }
        
        // only forward the message to the React application when the message comes from the parent window
        if (event.source === window.parent) {
            // use dispatchEvent instead of postMessage to avoid circular messages
            const customEvent = new CustomEvent('emailMessage', { detail: event.data });
            window.dispatchEvent(customEvent);
        }
    }
}); 