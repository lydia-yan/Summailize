import React, { useState, useEffect } from 'react';
import FirstTimeUserView from './components/FirstTimeUserView';
import DailyUserView from './components/DailyUserView';
import './styles/App.css';

function App() {
  const [isFirstTimeUser, setIsFirstTimeUser] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if the user is a first-time user
    const checkFirstTimeUser = async () => {
      try {
        setTimeout(() => {
          const userSettings = localStorage.getItem('emailSummarySettings');
          setIsFirstTimeUser(!userSettings);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Failed to load user settings:', error);
        setLoading(false);
      }
    };

    checkFirstTimeUser();
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