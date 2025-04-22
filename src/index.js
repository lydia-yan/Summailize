import React from 'react';
import ReactDOM from 'react-dom/client';
import { createTheme, ThemeProvider, initializeIcons } from '@fluentui/react';
import './styles/index.css';
import App from './App';

// Use strict icon registration options to completely disable warnings and prevent duplicate registration
const iconConfig = {
  disableWarnings: true,
  enableMemoizationForMarker: true, // Enable marker memoization
  initialState: {}
};

// Create custom theme to ensure consistent icon styling
const theme = createTheme({
  components: {
    Icon: {
      styles: {
        root: {
          fontWeight: 'normal',
          fontStyle: 'normal',
        }
      }
    }
  }
});

// Only initialize icons if not already initialized
if (!window.__fluentUIIcons) {
  window.__fluentUIIcons = true;
  console.log('Initializing Fluent UI icons');
  initializeIcons(undefined, iconConfig);
}

// Render the application
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <App />
    </ThemeProvider>
  </React.StrictMode>
); 