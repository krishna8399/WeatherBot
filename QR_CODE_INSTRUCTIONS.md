# How to Add a Real QR Code to Your Presentation

## Quick Method (Online)

1. **Go to any QR code generator:**
   - https://qr.io
   - https://www.qr-code-generator.com
   - https://www.the-qr-code-generator.com

2. **Enter your GitHub URL:**
   ```
   https://github.com/krishna8399/WeatherBot
   ```

3. **Download the QR code image** (PNG or SVG)

4. **Save it as:** `c:\WeatherBot\qr-code.png`

5. **Update the presentation:**
   - Open `presentation.html`
   - Find the line with `[QR CODE]`
   - Replace it with:
   ```html
   <img src="qr-code.png" style="width: 120px; height: 120px; border-radius: 5px;">
   ```

## Alternative: Use Python to Generate

If you want to generate it programmatically:

```python
pip install qrcode[pil]

# Then run:
import qrcode

qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data('https://github.com/krishna8399/WeatherBot')
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("qr-code.png")
```

## For Live Demo QR Code

If you deploy your bot online (e.g., via ngrok, Heroku, or AWS):

1. Get your live URL (e.g., `https://weatherbot-demo.herokuapp.com`)
2. Generate a QR code for that URL
3. Add a second QR code section in the presentation for the live demo

## Tips

- Use **high resolution** QR codes (at least 300x300px)
- Test the QR code with your phone before presenting
- Consider using a **URL shortener** (bit.ly, tinyurl) for cleaner QR codes
- You can customize QR code colors to match your presentation theme (purple/blue)
