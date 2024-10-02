import qrcode
import os
from consts import GetBoothNameTable, GetOutputDir, GetAdminAccessCode, GetAssetDir
from PIL import Image

def GetQrCodeAssetPath():
    return os.path.join(GetAssetDir(), "qrcodeIcons") 

def GetIconWithName(name):
    path = os.path.join(GetQrCodeAssetPath(), name+".png")
    if os.path.exists(path):
        return path
    return None
    
def GenerateAllQrCodes():
    for code, boothName in GetBoothNameTable().items():
        data = f"{GetServerURL()}/?c={code}"
        GenerateQrCode(boothName, data)

    data = f"{GetServerURL()}/?c={GetAdminAccessCode()}"
    GenerateQrCode("Admin",data)

def GetServerURL():
    return "http://3.137.157.79:8501"

def GenerateQrCode(codeFileName, data):
    
    # Create a QR code object
    qr = qrcode.QRCode(
        version=2,  # controls the size of the QR Code (1 is the smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # controls error correction
        box_size=10,  # size of the box where QR code will be displayed
        border=4,  # border size around the QR code
    )

    # Add data to the QR code
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR code
    qrCodeImg = qr.make_image(fill="black", back_color="white").convert("RGB")

    # Find and attach Icon
    iconPath = GetIconWithName(codeFileName)
    if iconPath:
        qrCodeCenterIcon = Image.open(iconPath)
        qrWidth, qrHeight = qrCodeImg.size
        iconSize = qrWidth//4
        qrCodeCenterIcon = qrCodeCenterIcon.resize((iconSize, iconSize), Image.Resampling.LANCZOS)
        iconPos = ((qrWidth - iconSize)//2, (qrHeight - iconSize)//2)
        qrCodeImg.paste(qrCodeCenterIcon, iconPos, mask = qrCodeCenterIcon)

    # Save the image file
    qrCodeImg.save(os.path.join(GetOutputDir(), codeFileName+".png"))

GenerateAllQrCodes()