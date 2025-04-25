### **Single Email Summarization Flow (Backend Overview)**



1. **Frontend sends a POST request**

   The frontend submits a request to /api/summarize/per with a JSON payload containing the emailUrl and userId.

2. **Flask route handles the request**

   The request is processed by a route defined in routes.py, which delegates the logic to summary_service.py.

3. **summary_service.py orchestrates the summarization process**

   It parses the Gmail message ID from the URL, loads user-specific settings (such as time zone and display preferences), and checks whether the email summary already exists in the EmailCache database.

4. **fetch_emails.py retrieves and cleans the email**
          
   This module uses the Gmail API to fetch the email contents. It decodes the message body, extracts key metadata (subject, sender, attachments), and formats the timestamp using utilities from time_utils.py.

5. **AI client.py calls the AI summarizer**

   The cleaned email body is sent to the summarization agent (Jenny), which returns a concise summary of the content.

6. **Summary is saved to the database**

   The completed summary, along with email metadata, is cached in the EmailCache table to avoid redundant processing.

7. **Structured JSON is returned to the frontend**

   The final response includes the subject, sender, timestamp, attachments, and the summary.



### **How to Test the Code**



1. **Prepare prerequisites**:

   

   - Make sure you have valid Gmail OAuth credentials (client_secret.json and token.json)
   - Start a local AI summarizer service (or use a mock endpoint)

   Run command: `python fetch_emails.py`

   

   

