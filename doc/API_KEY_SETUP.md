# API Key Setup Guide

## Easy Way to Save Your Google API Key

You now have **two ways** to save your API key so you don't need to enter it every time:

### Method 1: Using the UI (Easiest)
1. Run the app: `streamlit run frontend.py`
2. Enter your Google API Key in the sidebar
3. Click the **💾 Save Key** button
4. Your key is now saved to `.env` file
5. Next time you run the app, it will automatically load!

### Method 2: Manual Setup
1. Create a `.env` file in the project root (if it doesn't exist)
2. Add this line:
   ```
   GOOGLE_API_KEY="your-actual-api-key-here"
   ```
3. Save the file
4. Restart the app

## Managing Your API Key

### Clear Saved Key
- Click the **🗑️ Clear Key** button in the sidebar
- This removes the key from memory and the `.env` file

### Security Notes
- ✅ The `.env` file is already in `.gitignore` (won't be committed to git)
- ✅ The API key is stored locally on your machine
- ✅ Never share your `.env` file with others
- ✅ The password field hides your key in the UI

## How It Works

The app now:
1. Checks for saved API key in `.env` file on startup
2. Loads it automatically if found
3. Stores it in session state during your session
4. You can save it with one click using the Save button

**No more typing your API key every time!** 🎉
