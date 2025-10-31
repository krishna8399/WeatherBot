import qrcode

# Generate QR code for GitHub repository
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data('https://github.com/krishna8399/WeatherBot')
qr.make(fit=True)

# Create image with custom colors (purple theme)
img = qr.make_image(fill_color="#764ba2", back_color="white")
img.save("qr-code.png")

print("✅ QR code generated successfully: qr-code.png")
print("📱 Scan to access: https://github.com/krishna8399/WeatherBot")
