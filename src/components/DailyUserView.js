import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Text, 
  Stack, 
  PrimaryButton, 
  IconButton,
  Separator
} from '@fluentui/react';
import { mockData } from '../config/mockData';
import { sectionStyles, headerStyles, subtitleStyles, textStyles } from '../styles/common';

// Get mock data based on language
const { emailSummary: mockEmailSummary, periodicSummary: mockPeriodicSummary } = mockData.en;

// add a function to get the user email
const getUserEmail = () => {
  // prefer localStorage to keep the session consistency
  const savedEmail = localStorage.getItem('userEmail');
  console.log('getUserEmail, localStorage email:', savedEmail);
  if (savedEmail) return savedEmail;
  
  console.log('no email is found, use the default value');
  return "default_user"; // if no email is found, use the default value
};

/**
 * Send email URL to backend API
 * When a user opens an email, this function is called
 * @param {string} emailUrl - Email URL
 * @param {object} userSettings - User settings
 * @returns {Promise<object>} Returns API response
 */
/** 
const sendEmailUrlToBackend = async () => {
  const emailInfo = grabEmailInfo();
  console.log('Getting email summary, JSON data:', emailInfo);

  // Quick validation
  if (!emailInfo.subject || !emailInfo.sender || !emailInfo.received_date) {
    console.error("❌ Missing required fields. Maybe the email is not fully loaded yet.");
    return;
  }
  
  try {
    const userId = getUserEmail();

    const requestBody = {
      subject: emailInfo.subject,
      sender: emailInfo.sender,
      received_date: emailInfo.received_date,
      user_id: userId
    };
    
    console.log('Sending request body ...');
    const response = await fetch('http://localhost:8000/api/summarize/per', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    }).then(response => {
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Got Email summary result:', data);
    })
    .catch(error => {
      console.error('Failed to send email info:', error);
    });
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};
*/
/**
 * get periodic email summary
 * @returns {Promise<object>} return periodic summary data
 */
const fetchPeriodicSummary = async () => {
  try {
    console.log('get periodic summary');
    
    const userEmail = getUserEmail();
    console.log('Using user email:', userEmail);

    // call the actual API
    const response = await fetch('http://localhost:8000/api/summarize/overall', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      // use the user email as userId
      body: JSON.stringify({userId: userEmail})
    });
    
    // check the response status
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    // return the actual data
    return await response.json();
    
  } catch (error) {
    console.error('get periodic summary failed:', error);
    throw error;
  }
};

/**
 * calculate the next trigger time for summary update
 * @param {object} userSettings - user settings
 * @returns {number} the time difference to the next trigger (milliseconds)
 */
const calculateNextTriggerTime = (userSettings) => {
  const now = new Date();
  const currentHour = now.getHours();
  const currentDay = now.getDay(); // 0 is Sunday, 1-6 is Monday to Saturday
  
  const isWeekday = currentDay >= 1 && currentDay <= 5;
  
  const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  const currentDayName = dayNames[currentDay];
  
  const isSelectedWeekday = isWeekday && userSettings.weekdays?.includes(currentDayName);
  
  // get the time should be triggered today
  let triggerTime = null;
  if (isSelectedWeekday) {
    triggerTime = userSettings.weekdayTimes?.[0] || '09:00';
  } else if (!isWeekday) {
    triggerTime = userSettings.weekendTime || '11:00';
  }
  
  if (!triggerTime) {
    let nextDay = new Date(now);
    let nextTriggerTime = null;
    
    // check the next 7 days
    for (let i = 0; i < 7; i++) {
      nextDay.setDate(nextDay.getDate() + 1);
      const nextDayIndex = nextDay.getDay();
      const nextDayName = dayNames[nextDayIndex];
      const isNextWeekday = nextDayIndex >= 1 && nextDayIndex <= 5;
      
      if (isNextWeekday && userSettings.weekdays?.includes(nextDayName)) {
        nextTriggerTime = userSettings.weekdayTimes?.[0] || '09:00';
        break;
      } else if (!isNextWeekday) {
        nextTriggerTime = userSettings.weekendTime || '11:00';
        break;
      }
    }
    
    if (nextTriggerTime) {
      const [hours] = nextTriggerTime.split(':').map(Number);
      nextDay.setHours(hours, 0, 0, 0);
      return nextDay.getTime() - now.getTime();
    }
    
    // if no next trigger time is found, default to 24 hours later
    return 24 * 60 * 60 * 1000;
  }
  const [hours] = triggerTime.split(':').map(Number);
  const triggerDate = new Date(now);
  triggerDate.setHours(hours, 0, 0, 0);
  
  if (triggerDate.getTime() <= now.getTime()) {
    triggerDate.setDate(triggerDate.getDate() + 1);
  }
  
  return triggerDate.getTime() - now.getTime();
};

const DailyUserView = ({ onReturnToSettings }) => {
  // use useRef to store all the states that may trigger a re-render
  const stateRef = useRef({
    loading: false,
    currentEmailSummary: null,
    phaseSummary: null,
    userSettings: JSON.parse(localStorage.getItem('emailSummarySettings')) || {},
    summaryDateTime: '',
    isPhaseVisible: true,
    isPhaseCollapsed: false,
    emailProcessingError: null,
    lastHandledEmailId: null
  });
  
  // use useState to store the states that need to trigger a UI update
  const [uiState, setUiState] = useState(stateRef.current);
  
  // the function to update the states, also update the ref and UI
  const updateState = useCallback((updates) => {
    Object.assign(stateRef.current, updates);
    setUiState({...stateRef.current});
  }, []);
  
  // add email listener, receive email info from contentScript
  useEffect(() => {
    function handleEmailMessage(event) {
      if (event.data && event.data.type === 'USER_EMAIL') {
        const email = event.data.email;
        if (email) {
          console.log('after receiving the email info, fetch the data');
          localStorage.setItem('userEmail', email);
          
          // after receiving the email info, immediately fetch the data
          fetchPeriodicSummary()
            .then(summary => {
              if (summary) {
                updateState({
                  phaseSummary: summary,
                  summaryDateTime: summary.dateTime || '',
                  isPhaseVisible: true,
                  emailProcessingError: null
                });
              }
            })
            .catch(error => {
              console.error('after receiving the email info, fetch the data failed:', error);
            });
        }
      }
    }
    
    window.addEventListener('message', handleEmailMessage);
    
    return () => {
      window.removeEventListener('message', handleEmailMessage);
    };
  }, []);
  
  // the function to handle the messages
  const handleMessage = useCallback((event) => {
    const messageData = event instanceof CustomEvent ? event.detail : event.data;
    
    console.log('receive message:', messageData?.type);
    
    // handle the CURRENT_EMAIL type message
    if (messageData?.type === 'CURRENT_EMAIL' && messageData?.emailId) {
      const emailId = messageData.emailId;
      if (emailId === stateRef.current.lastHandledEmailId) return;
      
      stateRef.current.lastHandledEmailId = emailId;
      stateRef.current.loading = true;
      setUiState({...stateRef.current});
      
      console.log('📤 Sending TRIGGER_SEND_EMAIL to parent window');
      // Send to parent window (Gmail page)
      if (window.parent && window.parent !== window) {
          window.parent.postMessage({ type: 'TRIGGER_SEND_EMAIL' }, 'https://mail.google.com');
      } else {
          console.log('⚠️ No parent window, sending to self');
          window.postMessage({ 
            type: 'TRIGGER_SEND_EMAIL'
          }, window.location.origin);
      }
    }
    // handle the EMAIL_SUMMARY_RESPONSE type message
    else if (messageData?.type === 'EMAIL_SUMMARY_RESPONSE' && messageData?.data) {
      console.log('📩 receive EMAIL_SUMMARY_RESPONSE:', messageData.data);
      updateState({
        currentEmailSummary: messageData.data,
        loading: false,
        emailProcessingError: null
      });
    }
    // handle the possible error message
    else if (messageData?.type === 'EMAIL_SUMMARY_ERROR') {
      console.error('❌ email summary error:', messageData.error);
      updateState({
        loading: false,
        emailProcessingError: messageData.error || 'get email summary failed'
      });
    }
  }, [updateState]);

  
  // only set the message listener once when the component is mounted
  useEffect(() => {
    // listen to the custom event
    window.addEventListener('emailMessage', handleMessage);
    // keep listening to the postMessage to be compatible with other messages
    window.addEventListener('message', handleMessage);
    
    // load the periodic summary
    fetchPeriodicSummary()
      .then(summary => {
        if (summary) {
          Object.assign(stateRef.current, {
            phaseSummary: summary,
            summaryDateTime: summary.dateTime || ''
          });
          setUiState({...stateRef.current});
        }
      })
      .catch(error => {
        console.error('load periodic summary failed:', error);
      });
  
    
    // set the logic to trigger the summary update based on the user's time
    const scheduleNextUpdate = () => {
      const delay = calculateNextTriggerTime(stateRef.current.userSettings);
      setTimeout(() => {
        fetchPeriodicSummary()
          .then(summary => {
            if (summary) {
              Object.assign(stateRef.current, {
                phaseSummary: summary,
                summaryDateTime: summary.dateTime || '',
                isPhaseVisible: true
              });
              setUiState({...stateRef.current});
            }
          })
          .catch(error => {
            console.error('get summary by time failed:', error);
          })
          .finally(() => {
            // schedule the next update
            scheduleNextUpdate();
          });
      }, delay);
    };
    
    // start the timer
    scheduleNextUpdate();
    
    return () => {
      window.removeEventListener('emailMessage', handleMessage);
      window.removeEventListener('message', handleMessage);
      // clearInterval(checkInterval);
    };
  }, []);
  
  // refresh the summaries
  const handleRefreshSummaries = useCallback(async () => {
    try {
      setUiState(prev => ({ ...prev, loading: true }));
      const summary = await fetchPeriodicSummary();
      setUiState(prev => ({ 
        ...prev,
        phaseSummary: summary,
        summaryDateTime: summary?.dateTime || '',
        isPhaseVisible: true,
        loading: false,
        emailProcessingError: null
      }));
    } catch (error) {
      console.error('refresh summary failed:', error);
      setUiState(prev => ({ 
        ...prev,
        loading: false,
        emailProcessingError: 'refresh failed: ' + error.message
      }));
    }
  }, []);
  
  // handle the close of the periodic summary
  const handleClosePhaseSummary = useCallback(() => {
    setUiState(prev => ({ ...prev, isPhaseVisible: false }));
  }, []);
  
  // handle the toggle of the phase summary
  const handleTogglePhaseSummary = useCallback(() => {
    setUiState(prev => ({ 
      ...prev, 
      isPhaseCollapsed: !prev.isPhaseCollapsed 
    }));
  }, []);
  
  // return to the settings page
  const handleReturnToSettings = useCallback(() => {
    if (onReturnToSettings) {
      onReturnToSettings();
    }
  }, [onReturnToSettings]);
  
  // render the UI part
  return (
    <Stack tokens={{ childrenGap: 16 }} className="daily-view-container" style={{ marginTop: '40px' }}>
      {/* Settings button */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', position: 'absolute', top: '40px', right: '10px' }}>
        <IconButton
          iconProps={{ iconName: 'Settings' }}
          title="Settings"
          ariaLabel="Go to settings"
          onClick={handleReturnToSettings}
        />
      </div>
      
      {/* Phase summary section */}
      {uiState.phaseSummary && uiState.isPhaseVisible && (
        <div className={sectionStyles}>
          <div className={headerStyles}>
            <Text variant="large" className={textStyles.title}>{uiState.phaseSummary.title}</Text>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <IconButton
                iconProps={{ iconName: uiState.isPhaseCollapsed ? 'ChevronDown' : 'ChevronUp' }}
                title={uiState.isPhaseCollapsed ? "Expand summary" : "Collapse summary"}
                ariaLabel={uiState.isPhaseCollapsed ? "Expand summary" : "Collapse summary"}
                onClick={handleTogglePhaseSummary}
                styles={{ root: { marginRight: '4px' } }}
              />
              <IconButton
                iconProps={{ iconName: 'Cancel' }}
                title="Close summary"
                ariaLabel="Close summary"
                onClick={handleClosePhaseSummary}
              />
            </div>
          </div>
          
          {uiState.summaryDateTime && (
            <Text className={subtitleStyles}>{uiState.summaryDateTime}</Text>
          )}
          
          {!uiState.isPhaseCollapsed && (
            <div style={{ marginTop: '16px' }}>
              {uiState.phaseSummary.items.map(item => (
                <div key={item.id} style={{ marginBottom: '12px' }}>
                  <Text variant="mediumPlus" className={textStyles.category}>{item.category}</Text>
                  <Text className={textStyles.content}>{item.summary_bullets}</Text>
                  <Text className={textStyles.content}>{item.attachments}</Text>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {(!uiState.phaseSummary || !uiState.isPhaseVisible) && <div style={{ height: '20px' }} />}
      
      {uiState.phaseSummary && uiState.isPhaseVisible && <Separator />}
      
      {/* Current email summary section */}
      <div className={sectionStyles}>
        <div className={headerStyles}>
          <Text variant="large" className={textStyles.title}>Current Email Summary</Text>
        </div>
        
        {/* show the loading status */}
        {uiState.loading && !uiState.currentEmailSummary && (
          <div style={{ padding: '20px', textAlign: 'center' }}>
            <Text>Loading email summary...</Text>
          </div>
        )}
        
        {/* show the error status */}
        {uiState.emailProcessingError && !uiState.loading && (
          <div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#FFF4CE', color: '#333' }}>
            <Text>Error processing email: {uiState.emailProcessingError}</Text>
          </div>
        )}
        
        {/* show the email summary - keep the current summary even when loading new data */}
        {uiState.currentEmailSummary ? (
          <div style={{ padding: '8px 0', opacity: uiState.loading ? 0.7 : 1 }}>
            <Text variant="mediumPlus" style={{ fontWeight: 600, display: 'block', marginBottom: '8px' }}>
              {uiState.currentEmailSummary.subject}
            </Text>
            <Text style={{ display: 'block', marginBottom: '8px' }}>
              <span style={{ fontWeight: 500 }}>From:</span> {uiState.currentEmailSummary.sender_name}
            </Text>
            <Text block style={{ lineHeight: '1.5' }}>
              {uiState.currentEmailSummary.summary}
            </Text>
            {uiState.loading && (
              <div style={{ marginTop: '10px', textAlign: 'center', fontSize: '14px', color: '#666' }}>
                <Text>Updating...</Text>
              </div>
            )}
          </div>
        ) : !uiState.loading ? (
          <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
            <Text>Open a mail to view its summary</Text>
          </div>
        ) : null}
      </div>
      
      {/* Refresh button */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '12px' }}>
        <PrimaryButton 
          text="Refresh Summary" 
          onClick={handleRefreshSummaries}
          disabled={uiState.loading} 
        />
      </div>
    </Stack>
  );
};


export default DailyUserView; 