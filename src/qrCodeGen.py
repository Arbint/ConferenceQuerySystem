import qrcode
import os
from database import GetBoothNameTable, GetOutputDir, GetAdminAccessCode

def GenerateAllQrCodes():
    for code, boothName in GetBoothNameTable().items():
        GenerateQrCode(boothName, code)

    GenerateQrCode("Admin", GetAdminAccessCode())

def GetServerURL():
    return "http://3.137.157.79:8501"

def GenerateQrCode(codeFileName, accessCode):
    data = f"{GetServerURL()}/?c={accessCode}"
    
    # Create a QR code object
    qr = qrcode.QRCode(
        version=2,  # controls the size of the QR Code (1 is the smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # controls error correction
        box_size=10,  # size of the box where QR code will be displayed
        border=4,  # border size around the QR code
    )

    # Add data to the QR code
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill="black", back_color="white")

    # Save the image file
    img.save(os.path.join(GetOutputDir(), codeFileName+".png"))

GenerateAllQrCodes()