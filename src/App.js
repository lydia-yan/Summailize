import React, { useState, useEffect } from 'react';
import FirstTimeUserView from './components/FirstTimeUserView';
import DailyUserView from './components/DailyUserView';
import './styles/App.css';

function App() {
  const [isFirstTimeUser, setIsFirstTimeUser] = useState(true);
  const [loading, setLoading] = useState(true);
  const [userEmail, setUserEmail] = useState(null);
  const [needLogin, setNeedLogin] = useState(true); 

  useEffect(() => {
    // add message listener, receive the email from Chrome extension
    function handleMessage(event) {
      if (event.data && event.data.type === 'oauth_success') {
        const email = event.data.email;
        if (email) {
          console.log('App component, receive the email:', email);
          localStorage.setItem('userEmail', email);
          setUserEmail(email);

          const userSettings = localStorage.getItem('emailSummarySettings');
          if (userSettings) {
            setIsFirstTimeUser(false);
          } else {
            setIsFirstTimeUser(true); 
          }
          setNeedLogin(false);
          setLoading(false); 
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
            setNeedLogin(false);
          } else {
            setNeedLogin(true); // need to authorize
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

  const handleLogin = () => {
    // authorize the user
    const apiBaseUrl = "http://localhost:8000"; // auto catch localhost or extension domain: const apiBaseUrl = window.location.origin;
    const loginUrl = `${apiBaseUrl}/api/login`; 
    window.open(loginUrl, 'Login', 'width=600,height=600');
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (needLogin) {
    return (
      <div className="app-container">
        <h2>Welcome to Gmail Summary Extension</h2>
        <button className="login-button" onClick={handleLogin}>
          Sign in with Gmail
        </button>
      </div>
    );
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