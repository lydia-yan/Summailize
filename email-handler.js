// email-handler.js
console.log('📜 email-handler.js loaded');

// Format Date to "YYYY-MM-DD"
window.formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
};

// Grab Email Info from Gmail Page
window.grabEmailInfo = () => {
    const subjectElement = document.querySelector('.hP');
    const senderElement = document.querySelector('.gD');
    const receiverElement = document.querySelector('.g2');
    const receivedDateElement = document.querySelector('.g3');

    const subject = subjectElement?.innerText.trim() || "";
    const sender = senderElement?.getAttribute('email')?.trim() || "";
    const receiver = receiverElement?.getAttribute('email')?.trim() || "";
    const receivedDateRaw = receivedDateElement?.getAttribute('title') || "";
    const received_date = receivedDateRaw ? window.formatDate(receivedDateRaw) : "";

    console.log('📦 grabEmailInfo:', { subject, sender, receiver, received_date });

    return { subject, sender, receiver, received_date };
};


// Send Email Info to Backend API
window.sendEmailUrlToBackend = async () => {
    const emailInfo = grabEmailInfo();
    console.log('Getting email summary, JSON data:', emailInfo);

    if (!emailInfo.subject || !emailInfo.sender || !emailInfo.received_date) {
        console.error("❌ Missing required fields. Maybe the email is not fully loaded yet.");
        return;
    }

    try {
        const requestBody = {
            subject: emailInfo.subject,
            sender: emailInfo.sender,
            received_date: emailInfo.received_date,
            user_id: String(emailInfo.receiver).toLowerCase()
        };

        console.log('Sending request body ...', requestBody);
        const response = await fetch('http://localhost:8000/api/summarize/per', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();
        // If summary is empty, use subject as fallback
        if (!data.summary) {
            data.summary = data.subject;
        }
        console.log('✅ Got email summary result:', data);
        
        // send message to current window
        window.postMessage({ type: 'EMAIL_SUMMARY_RESPONSE', data }, '*');
        
        // send message to iframe
        const iframe = document.getElementById('aimail-email-summary-iframe');
        if (iframe && iframe.contentWindow) {
            console.log('📨 send EMAIL_SUMMARY_RESPONSE to iframe');
            iframe.contentWindow.postMessage({ type: 'EMAIL_SUMMARY_RESPONSE', data }, '*');
        } else {
            console.error('❌ cannot find iframe or its contentWindow');
        }
    } catch (error) {
        console.error('❌ API call failed:', error);
        window.postMessage({ type: 'EMAIL_SUMMARY_ERROR', error: error.message }, '*');
        
        // send error message to iframe
        const iframe = document.getElementById('aimail-email-summary-iframe');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({ type: 'EMAIL_SUMMARY_ERROR', error: error.message }, '*');
        }
    }
};
  
  
// Listen for Gmail messages
console.log('📡 Setting up message listener in email-handler.js');
window.addEventListener('message', function(event) {
    console.log('📩 email-handler.js received message:', event.data);
    if (event.data && event.data.type === 'TRIGGER_SEND_EMAIL') {
        console.log('✅ Received TRIGGER_SEND_EMAIL');
        setTimeout(() => {
            if (window.sendEmailUrlToBackend) {
                console.log('🚀 Calling sendEmailUrlToBackend');
                window.sendEmailUrlToBackend();
            } else {
                console.error('❌ sendEmailUrlToBackend is not defined');
            }
        }, 2000);
    }
});
  