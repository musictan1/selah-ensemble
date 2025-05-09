@echo off
echo Generating QR code for Sela Ensemble Website...
echo.

REM Replace with your Netlify URL after deployment
set WEBSITE_URL=https://[YOUR-NETLIFY-URL].netlify.app

REM Generate QR code using qrcode.js
echo ^<!DOCTYPE html^> > qr.html
echo ^<html^> >> qr.html
echo ^<head^> >> qr.html
echo ^<title^>Sela Ensemble QR Code^</title^> >> qr.html
echo ^<script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.1/build/qrcode.min.js"^>^</script^> >> qr.html
echo ^</head^> >> qr.html
echo ^<body style="text-align: center; margin-top: 50px;"^> >> qr.html
echo ^<h2^>Sela Ensemble Website QR Code^</h2^> >> qr.html
echo ^<div id="qrcode"^>^</div^> >> qr.html
echo ^<p^>Scan this QR code to visit our website^</p^> >> qr.html
echo ^<script^> >> qr.html
echo QRCode.toCanvas(document.getElementById('qrcode'), '%WEBSITE_URL%', function (error) { >> qr.html
echo     if (error) console.error(error) >> qr.html
echo     console.log('success!'); >> qr.html
echo }); >> qr.html
echo ^</script^> >> qr.html
echo ^</body^> >> qr.html
echo ^</html^> >> qr.html

echo QR code generated! Opening in browser...
start qr.html 