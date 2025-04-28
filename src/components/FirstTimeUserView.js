import React, { useState, useEffect } from 'react';
import { 
  Text, 
  Stack, 
  PrimaryButton, 
  Dropdown, 
  Label, 
  ComboBox,
  DefaultButton
} from '@fluentui/react';

const timeZones = [
  { key: 'UTC-12:00', text: '(UTC-12:00) International Date Line West' },
  { key: 'UTC-11:00', text: '(UTC-11:00) Coordinated Universal Time-11' },
  { key: 'UTC-10:00', text: '(UTC-10:00) Hawaii' },
  { key: 'UTC-09:00', text: '(UTC-09:00) Alaska' },
  { key: 'UTC-08:00', text: '(UTC-08:00) Pacific Time (US & Canada)' },
  { key: 'UTC-07:00', text: '(UTC-07:00) Mountain Time (US & Canada)' },
  { key: 'UTC-06:00', text: '(UTC-06:00) Central Time (US & Canada)' },
  { key: 'UTC-05:00', text: '(UTC-05:00) Eastern Time (US & Canada)' },
  { key: 'UTC-04:00', text: '(UTC-04:00) Atlantic Time (Canada)' },
  { key: 'UTC-03:00', text: '(UTC-03:00) Brasilia' },
  { key: 'UTC-02:00', text: '(UTC-02:00) Coordinated Universal Time-02' },
  { key: 'UTC-01:00', text: '(UTC-01:00) Azores' },
  { key: 'UTC+00:00', text: '(UTC+00:00) Dublin, Edinburgh, Lisbon, London' },
  { key: 'UTC+01:00', text: '(UTC+01:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Vienna' },
  { key: 'UTC+02:00', text: '(UTC+02:00) Helsinki, Kyiv, Riga, Sofia, Tallinn, Vilnius' },
  { key: 'UTC+03:00', text: '(UTC+03:00) Moscow, St. Petersburg, Volgograd' },
  { key: 'UTC+08:00', text: '(UTC+08:00) Beijing, Chongqing, Hong Kong, Urumqi' },
];

const days = [
  { key: 'monday', text: 'Monday' },
  { key: 'tuesday', text: 'Tuesday' },
  { key: 'wednesday', text: 'Wednesday' },
  { key: 'thursday', text: 'Thursday' },
  { key: 'friday', text: 'Friday' },
  { key: 'saturday', text: 'Saturday' },
  { key: 'sunday', text: 'Sunday' },
];

const times = [
  { key: 'none', text: 'None' },
  { key: '8:00 AM', text: '8:00 AM' },
  { key: '9:00 AM', text: '9:00 AM' },
  { key: '10:00 AM', text: '10:00 AM' },
  { key: '11:00 AM', text: '11:00 AM' },
  { key: '12:00 PM', text: '12:00 PM' },
  { key: '1:00 PM', text: '1:00 PM' },
  { key: '2:00 PM', text: '2:00 PM' },
  { key: '3:00 PM', text: '3:00 PM' },
  { key: '4:00 PM', text: '4:00 PM' },
  { key: '5:00 PM', text: '5:00 PM' },
  { key: '6:00 PM', text: '6:00 PM' },
];

// add a function to get the user email
const getUserEmail = () => {
  // prefer localStorage to keep the session consistency
  const savedEmail = localStorage.getItem('userEmail');
  console.log('FirstTimeUserView, check the localStorage email:', savedEmail);
  if (savedEmail) return savedEmail;
  
  console.log('FirstTimeUserView, no email is found, use the default value');
  return "default_user"; // if no email is found, use the default value
};

/**
 * Send user settings to backend
 * @param {object} settings - user settings
 * @returns {Promise<object>} backend response
 */
const sendSettingsToBackend = async (settings) => {
  try {
    console.log('Sending settings to backend:', JSON.stringify(settings));
    
    // the real API call
    const response = await fetch('http://localhost:8000/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    });
    return await response.json();
  } catch (error) {
    console.error('Failed to send settings to backend:', error);
    throw error;
  }
};

const FirstTimeUserView = ({ onSaveSettings }) => {
  const [weekdayTime, setWeekdayTime] = useState('9:00 AM');
  const [weekendTime, setWeekendTime] = useState('11:00 AM');
  const [selectedTimeZone, setSelectedTimeZone] = useState('UTC+08:00');
  const [selectedWeekdays, setSelectedWeekdays] = useState(['monday', 'tuesday', 'wednesday', 'thursday', 'friday']);
  const [isSaving, setIsSaving] = useState(false);
  
  // add email listener, receive email info from contentScript
  useEffect(() => {
    function handleEmailMessage(event) {
      if (event.data && event.data.type === 'USER_EMAIL') {
        const email = event.data.email;
        if (email) {
          console.log('FirstTimeUserView, receive the email:', email);
          // save the email to localStorage
          localStorage.setItem('userEmail', email);
          // force the component to re-render to update the display
          setIsSaving(false); // use a existing state to trigger the re-render
        }
      }
    }
    
    window.addEventListener('message', handleEmailMessage);
    
    return () => {
      window.removeEventListener('message', handleEmailMessage);
    };
  }, []);

  const handleSaveSettings = async () => {
    try {
      setIsSaving(true);
      
      // get the user email
      const userEmail = getUserEmail();
      console.log('FirstTimeUserView, save the settings using the email:', userEmail);
      
      // create user settings object, keep the original format
      const settings = {
        weekdayTime: weekdayTime,
        weekendTime: weekendTime,
        timeZone: selectedTimeZone,
        weekdays: selectedWeekdays,
        userId: userEmail // add the user email as userId
      };

      // save to local storage
      localStorage.setItem('emailSummarySettings', JSON.stringify(settings));

      // send to backend
      await sendSettingsToBackend(settings);

      // notify parent component
      onSaveSettings(settings); 
      
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const onTimeZoneChange = (event, option) => {
    setSelectedTimeZone(option.key);
  };

  const onWeekdaysChange = (event, option) => {
    if (option.selected) {
      setSelectedWeekdays([...selectedWeekdays, option.key]);
    } else {
      setSelectedWeekdays(selectedWeekdays.filter(day => day !== option.key));
    }
  };

  const onWeekdayTimeChange = (event, option) => {
    setWeekdayTime(option.key);
  };

  const onWeekendTimeChange = (event, option) => {
    setWeekendTime(option.key);
  };

  // custom button styles
  const customButtonStyles = {
    root: {
      backgroundColor: '#0b57d0',
      borderRadius: '8px',
      padding: '0 24px',
      height: '40px !important',
      transition: 'all 0.2s ease',
    },
    rootHovered: {
      backgroundColor: '#1a73e8',
    },
    label: {
      fontWeight: 600,
      fontSize: '15px'
    }
  };
  
  // custom dropdown styles
  const dropdownStyles = {
    dropdown: { 
      width: '100%',
      selectors: {
        '.ms-Dropdown-title': {
          borderRadius: '6px'
        }
      }
    }
  };
  
  const timeDropdownStyles = {
    dropdown: { 
      width: '50%',
      selectors: {
        '.ms-Dropdown-title': {
          borderRadius: '6px'
        }
      }
    }
  };

  return (
    <Stack tokens={{ childrenGap: 24 }} style={{ marginTop: '40px', padding: '0 0' }}>
      <Text variant="xLarge" block style={{ fontWeight: 600, fontSize: '24px', marginBottom: '8px' }}>
        Welcome to Email Digest Assistant
      </Text>
      <Text style={{ fontSize: '15px', lineHeight: '1.5', marginBottom: '12px' }}>
        Please set up when you would like to receive email digests. We'll automatically provide you with summaries based on your preferences.
      </Text>

      <div className="settings-group" style={{ marginTop: '12px' }}>
        <Label style={{ marginBottom: '8px', fontSize: '15px' }}>Time Zone</Label>
        <Dropdown
          placeholder="Select your time zone"
          options={timeZones}
          selectedKey={selectedTimeZone}
          onChange={onTimeZoneChange}
          styles={dropdownStyles}
        />
      </div>

      <div className="settings-group" style={{ marginTop: '8px' }}>
        <Label style={{ marginBottom: '8px', fontSize: '15px' }}>Weekday Digest Time</Label>
        <Dropdown
          placeholder="Select time"
          options={times}
          selectedKey={weekdayTime}
          onChange={onWeekdayTimeChange}
          styles={timeDropdownStyles}
        />
        
        <div style={{ marginTop: 16 }}>
          <Label style={{ marginBottom: '8px', fontSize: '15px' }}>Weekdays</Label>
          <ComboBox
            multiSelect
            options={days.filter(day => day.key !== 'saturday' && day.key !== 'sunday')}
            selectedKey={selectedWeekdays}
            onChange={onWeekdaysChange}
            styles={dropdownStyles}
          />
        </div>
      </div>

      <div className="settings-group" style={{ marginTop: '8px' }}>
        <Label style={{ marginBottom: '8px', fontSize: '15px' }}>Weekend Digest Time</Label>
        <Dropdown
          placeholder="Select time"
          options={times}
          selectedKey={weekendTime}
          onChange={onWeekendTimeChange}
          styles={timeDropdownStyles}
        />
      </div>

      <div className="button-container" style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
        <PrimaryButton 
          text={isSaving ? "Saving..." : "Save Settings"}
          onClick={handleSaveSettings}
          disabled={isSaving}
          styles={customButtonStyles}
        />
      </div>
    </Stack>
  );
};

export default FirstTimeUserView; 