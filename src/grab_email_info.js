// grab_email_info.js

// === Function: Format Date to "YYYY-MM-DD" ===
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toISOString().split('T')[0]; // Ex: 2024-04-27
  }
  
  // === Function: Grab Email Info from Gmail Page ===
  function grabEmailInfo() {
    const subject = document.querySelector('.hP')?.innerText || "";
    const sender = document.querySelector('.gD')?.getAttribute('email') || "";
    const receiver = document.querySelector('.g2')?.getAttribute('email') || "";
    const receivedDateRaw = document.querySelector('.g3')?.getAttribute('title') || "";
    const receivedDate = receivedDateRaw ? formatDate(receivedDateRaw) : "";
  
    return {
      subject,
      sender,
      receiver,
      received_date: receivedDate
    };
  }
  
  // === Function: Send Email Info to Backend API ===
  function sendEmailInfoToBackend(userId) {
    const emailInfo = grabEmailInfo();
  
    // Quick check
    if (!emailInfo.subject || !emailInfo.sender || !emailInfo.received_date) {
      console.error("❌ Missing required fields. Maybe this email is not fully loaded?");
      return;
    }
  
    fetch('http://127.0.0.1:8000/api/summarize/per', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        subject: emailInfo.subject,
        sender: emailInfo.sender,
        received_date: emailInfo.received_date,
        user_id: userId
      })
    })
    .then(response => response.json())
    .then(data => {
      console.log('✅ Email found:', data);
    })
    .catch(error => {
      console.error('❌ Error sending email info:', error);
    });
  }
  
  // === Example Usage ===
  // Wait 2 seconds after Gmail page loads (emails take time to render sometimes)
  setTimeout(() => {
    const yourUserId = "jennyc28@uci.edu"; // <-- Replace this!
    sendEmailInfoToBackend(yourUserId);
  }, 2000);
  
  