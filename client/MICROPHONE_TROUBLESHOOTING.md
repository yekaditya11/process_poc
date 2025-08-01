# Microphone Troubleshooting Guide

## Overview
The chatbot includes voice input functionality using the Web Speech Recognition API. This guide helps you troubleshoot common microphone issues.

## Common Issues and Solutions

### 1. **HTTPS Requirement**
**Problem**: Microphone access requires a secure context (HTTPS).

**Solution**: 
- For development: The app is now configured to run with HTTPS
- Run `npm start` - it will automatically use HTTPS
- Access via `https://localhost:3000` instead of `http://localhost:3000`

### 2. **Browser Compatibility**
**Problem**: Speech recognition is not supported in all browsers.

**Supported Browsers**:
- ✅ Chrome (recommended)
- ✅ Edge
- ✅ Safari
- ❌ Firefox (limited support)

**Solution**: Use Chrome, Edge, or Safari for best compatibility.

### 3. **Microphone Permissions**
**Problem**: Browser blocks microphone access.

**Solution**:
1. Click the microphone icon in the address bar
2. Select "Allow" for microphone access
3. Refresh the page if needed

### 4. **Hardware Issues**
**Problem**: Microphone not working at system level.

**Solution**:
1. Check if microphone works in other applications
2. Verify microphone is set as default input device
3. Test microphone in browser settings (chrome://settings/content/microphone)

## Testing Microphone Functionality

### Option 1: Use the Test Page
1. Navigate to `/test-microphone` in your app
2. Click "Run Microphone Tests"
3. Review the test results for specific issues

### Option 2: Browser Console Debugging
1. Open browser developer tools (F12)
2. Go to Console tab
3. Try using the microphone in the chatbot
4. Look for error messages

### Option 3: Manual Testing
1. Open the chatbot
2. Click the microphone button
3. Check for:
   - Permission prompts
   - Error messages
   - Visual feedback (recording indicator)

## Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Speech recognition not supported" | Browser doesn't support Web Speech API | Use Chrome, Edge, or Safari |
| "HTTPS required for microphone" | Running on HTTP instead of HTTPS | Use HTTPS or localhost |
| "Microphone permission denied" | Browser blocked microphone access | Allow microphone in browser settings |
| "No speech detected" | No audio input received | Speak clearly and check microphone |
| "Audio capture failed" | Hardware or driver issue | Check microphone in system settings |

## Development Setup

### Running with HTTPS
```bash
cd process_poc/client
npm start
```
The app will automatically run on HTTPS with a self-signed certificate.

### Testing Different Scenarios
1. **Local Development**: `https://localhost:3000`
2. **Production**: Must use HTTPS
3. **Mobile Testing**: Use HTTPS and allow microphone permissions

## Browser-Specific Instructions

### Chrome
1. Go to `chrome://settings/content/microphone`
2. Add your site to allowed sites
3. Ensure microphone is not blocked

### Safari
1. Go to Safari > Preferences > Websites > Microphone
2. Allow microphone access for your site

### Edge
1. Go to Settings > Cookies and site permissions > Microphone
2. Allow microphone access

## Debug Information

The enhanced microphone implementation includes:
- ✅ Secure context detection
- ✅ Browser compatibility checking
- ✅ Permission status tracking
- ✅ Detailed error messages
- ✅ Visual feedback for recording state
- ✅ Graceful fallbacks

## Quick Fix Checklist

- [ ] Running on HTTPS or localhost
- [ ] Using supported browser (Chrome/Edge/Safari)
- [ ] Microphone permissions allowed
- [ ] Microphone working in other apps
- [ ] No browser extensions blocking microphone
- [ ] Microphone set as default input device

## Still Having Issues?

1. **Check the test page**: Navigate to `/test-microphone` for detailed diagnostics
2. **Browser console**: Look for specific error messages
3. **Try different browser**: Test in Chrome, Edge, and Safari
4. **Check system audio**: Ensure microphone works in other applications
5. **Clear browser data**: Clear cookies and site data for your domain

## Technical Details

The microphone implementation uses:
- `navigator.mediaDevices.getUserMedia()` for permission handling
- `webkitSpeechRecognition` for Chrome/Edge
- `SpeechRecognition` for Safari
- Secure context validation
- Comprehensive error handling

For more technical details, see the `ChatInput.js` component. 