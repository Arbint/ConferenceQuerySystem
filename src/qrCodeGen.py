import qrcode
import os
from consts import GetBoothNameTable, GetOutputDir, GetAdminAccessCode, GetAssetDir
from PIL import Image, ImageOps
import math

def GetQrCodeAssetPath():
    path = os.path.join(GetAssetDir(), "qrcodeIcons") 
    path = os.path.normpath(path)
    if not os.path.exists(path):
        os.mkdir(path)

    return path

def GetQrCodeOutputPath():
    path = os.path.join(GetOutputDir(), "qrcodes")
    path = os.path.normpath(path)
    if not os.path.exists(path):
        os.mkdir(path)

    return path

def GetIconWithName(name):
    path = os.path.join(GetQrCodeAssetPath(), name+".png")
    if os.path.exists(path):
        return path
    return None
    
def GetDefaultIconPath():
    path = os.path.join(GetQrCodeAssetPath(), "Default.png")
    if os.path.exists(path):
        return os.path.normpath(path)
    return None

def GenerateAllQrCodes():
    for code, boothName in GetBoothNameTable().items():
        data = f"{GetServerURL()}/?c={code}"
        GenerateQrCode(boothName, data)

    data = f"{GetServerURL()}/?c={GetAdminAccessCode()}"
    GenerateQrCode("Admin",data)

def GetServerURL():
    return "http://3.137.157.79:8501"

def GetExistingQrCodes():
    qrCodeNames = os.listdir(GetQrCodeOutputPath())
    qrCodePaths = []
    for name in qrCodeNames:
        qrCodePath = os.path.join(GetQrCodeOutputPath(), name)
        qrCodePaths.append(os.path.normpath(qrCodePath))

    return qrCodePaths

def RemovePreviousQrCodes():
    for qrCode in GetExistingQrCodes():
        if not os.path.isdir(qrCode):
            os.remove(qrCode)
    
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
    if not iconPath:
        iconPath = GetDefaultIconPath()

    if iconPath:
        qrCodeCenterIcon = Image.open(iconPath)
        borderSize = 40
        qrCodeCenterIcon = ImageOps.expand(qrCodeCenterIcon, border=borderSize, fill=(255,100,0))
        qrWidth, qrHeight = qrCodeImg.size
        iconSize = qrWidth//4
        qrCodeCenterIcon = qrCodeCenterIcon.resize((iconSize, iconSize), Image.Resampling.LANCZOS)
        iconPos = ((qrWidth - iconSize)//2, (qrHeight - iconSize)//2)
        qrCodeImg.paste(qrCodeCenterIcon, iconPos, mask = qrCodeCenterIcon)

    # Save the image file
    qrCodeImg.save(os.path.join(GetQrCodeOutputPath(), codeFileName+".png"))

def CombineQrCodesIntoPdf():
    qrCodePaths = GetExistingQrCodes()
    images = [Image.open(image) for image in qrCodePaths]
    images[0].save(os.path.join(GetQrCodeOutputPath(),'allQrCodes.pdf'), save_all=True, append_images=images[1:])

def CombineQrCodeIntoImage(numOfColums = 3):
    qrCodePaths = GetExistingQrCodes()
    images = [Image.open(image) for image in qrCodePaths]

    imageCount = len(images)
    numOfRows = math.ceil(imageCount / numOfColums)

    totalWidth = max(img.width for img in images) * numOfColums
    totalHeight = max(img.width for img in images) * numOfRows

    combinedImage = Image.new("RGB", (totalWidth, totalHeight), color = (255,255,255))

    currentIndex = 0
    for y in range(numOfRows):
        for x in range(numOfColums):
            if currentIndex < len(images):
                image = images[currentIndex]
                combinedImage.paste(image, (x * image.width, y * image.height))
                currentIndex+=1

    combinedImage.save(os.path.join(GetQrCodeOutputPath(), "allQrCodes.png"))

if __name__ == "__main__":
    RemovePreviousQrCodes()
    GenerateAllQrCodes()
    CombineQrCodeIntoImage()