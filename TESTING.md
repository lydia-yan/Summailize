# Testing Guide

## Overview

This document outlines the testing procedures for the AIMAIL Chrome extension. Since the backend APIs are currently mocked, this guide focuses on frontend testing and API simulation.

## Setup for Testing

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run build
   ```

3. Load the extension in Chrome:
   - Go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `dist` directory

## Component Testing

### FirstTimeUserView
1. Test initial setup:
   - Verify all form fields are present
   - Check time picker functionality
   - Test timezone selection
   - Verify save button behavior

### DailyUserView
1. Test summary display:
   - Verify mock data is displayed correctly
   - Check timestamp formatting
   - Test refresh functionality

2. Test settings button:
   - Verify navigation to settings
   - Test return functionality

## API Testing

### Mocked APIs

The following APIs are currently mocked in the code:

1. Summary APIs:
2. Settings APIs:
3. Sending Email URL

## UI Testing
1. Test different screen sizes
2. Verify mobile responsiveness
3. Check component layout

