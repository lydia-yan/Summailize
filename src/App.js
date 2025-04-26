import React, { useState, useEffect } from 'react';
import FirstTimeUserView from './components/FirstTimeUserView';
import DailyUserView from './components/DailyUserView';
import './styles/App.css';

function App() {
  const [isFirstTimeUser, setIsFirstTimeUser] = useState(true);
  const [loading, setLoading] = useState(true);
  const [userEmail, setUserEmail] = useState(null);

  useEffect(() => {
    // add message listener, receive the email from Chrome extension
    function handleMessage(event) {
      if (event.data && event.data.type === 'USER_EMAIL') {
        const email = event.data.email;
        if (email) {
          console.log('App component, receive the email:', email);
          localStorage.setItem('userEmail', email);
          setUserEmail(email);
        }
      }
    }
    
    window.addEventListener('message', handleMessage);
    
    // Check if the user is a first-time user
    const checkFirstTimeUser = async () => {
      try {
        setTimeout(() => {
          const userSettings = localStorage.getItem('emailSummarySettings');
          // try to get the email from localStorage
          const savedEmail = localStorage.getItem('userEmail');
          if (savedEmail) {
            console.log('App component, get the email from localStorage:', savedEmail);
            setUserEmail(savedEmail);
          }
          
          setIsFirstTimeUser(!userSettings);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Failed to load user settings:', error);
        setLoading(false);
      }
    };

    checkFirstTimeUser();
    
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, []);

  const saveUserSettings = async (settings) => {
    try {
      // Only save to localStorage and update UI state
      localStorage.setItem('emailSummarySettings', JSON.stringify(settings));
      setIsFirstTimeUser(false);
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };
  
  const returnToSettings = () => {
    setIsFirstTimeUser(true);
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="app-container">
      {isFirstTimeUser ? (
        <FirstTimeUserView onSaveSettings={saveUserSettings} />
      ) : (
        <DailyUserView onReturnToSettings={returnToSettings} />
      )}
    </div>
  );
}

export default App; 