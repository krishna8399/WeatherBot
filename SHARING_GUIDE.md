# WeatherBot - Sharing Guide

## Quick Share on Local Network

### For You (Host):
1. Make sure bot is running:
   ```cmd
   .\start_bot.bat
   ```

2. Find your IP address:
   ```powershell
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

3. Share this URL with others:
   ```
   http://YOUR_IP:8080
   ```

4. Keep your computer on and the bot running!

### For Your Friends (Users):
1. Open a web browser
2. Go to: http://YOUR_IP:8080 (replace YOUR_IP with the actual IP)
3. Start chatting!

**No installation needed for users - just a browser!**

---

## Share Over Internet with ngrok

### Setup (One-time):
1. Download ngrok: https://ngrok.com/download
2. Sign up for free account
3. Extract ngrok.exe to a folder (e.g., C:\ngrok)

### Every Time You Want to Share:
1. Start your bot:
   ```cmd
   .\start_bot.bat
   ```

2. Open new PowerShell and run:
   ```powershell
   cd C:\ngrok
   .\ngrok http 8080
   ```

3. Copy the "Forwarding" URL shown (e.g., https://abc123.ngrok.io)

4. Share that URL with anyone!

### To Stop Sharing:
- Press Ctrl+C in the ngrok window
- Close the bot windows

---

## Firewall Setup (If needed)

If others can't connect on your local network:

1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Click "Change settings" (requires admin)
4. Click "Allow another app"
5. Browse to: `C:\Users\krish\anaconda3\envs\weather_env\python.exe`
6. Add it and check both Private and Public boxes
7. Click OK

---

## Keep Bot Running 24/7 (Optional)

### Option 1: Keep Your Computer On
- Disable sleep mode in Windows Power settings
- Keep the 3 CMD windows open
- Set your router to give your PC a static local IP

### Option 2: Use ngrok with Auto-restart
Create `start_with_ngrok.bat`:
```batch
@echo off
start "" .\start_bot.bat
timeout /t 20
start "" cmd /k "cd C:\ngrok && ngrok http 8080"
```

### Option 3: Cloud Deployment
- Deploy to Heroku, AWS, or DigitalOcean
- Bot runs 24/7 on a server
- No need to keep your computer on

---

## Sharing Checklist

Before sharing with others:

- [ ] Bot is running (3 CMD windows open)
- [ ] WEATHERAPI_KEY environment variable is set
- [ ] Firewall allows Python (if sharing on local network)
- [ ] You have the correct IP or ngrok URL
- [ ] Your computer will stay on while others use it

---

## Example Share Message

Copy this and send to friends:

```
Hi! Try out my WeatherBot:

🌐 Link: http://192.168.1.100:8080
(or your ngrok URL: https://abc123.ngrok.io)

Just open the link in your browser and start chatting!

Try asking:
- "weather in berlin"
- "will it rain in london?"
- "what's the humidity in paris?"

No installation needed! 🤖☀️
```

---

## Troubleshooting

**"Connection refused" error:**
- Make sure the bot is running
- Check firewall settings
- Verify the IP address is correct

**Others can't connect:**
- Are they on the same network? (for local sharing)
- Is Windows Firewall blocking it?
- Is the bot still running?

**ngrok URL doesn't work:**
- Make sure ngrok is running
- Check the ngrok window for the current URL
- Free tier URLs expire when ngrok closes

---

## Need Help?

- Test locally first: http://localhost:8080
- Check all 3 CMD windows are running without errors
- Make sure WEATHERAPI_KEY is set in environment variables
