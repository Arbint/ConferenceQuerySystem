import qrcode
import os
from conferencequerysystem.consts import GetBoothNameTable, GetOutputDir, GetAdminAccessCode, GetAssetDir
from conferencequerysystem.utilities import GetURLFromUser
from PIL import Image, ImageOps
import math
import sys


class QRCodeGen:
    def __init__(self,clientURL, adminURL, submissionServerURL):
        #TODO: Should maybe refactor this to be always aligned with the booth names defined in the const.py
        self.qrCodeIconColorDict = {
            "Animation_Demo": "#C10808",
            "Animation_Interactive":"#ff8989",

            "Modeling_Demo": "#239b56",
            "Modeling_Interactive":"#8aff80",

            "Programming_Demo": "#3d6ced",
            "Programming_Interactive":"#74b8f5",

            "Ballroom_Animation": "#0cc1e7",
            "Ballroom_Modeling": "#fbff00",
            "Ballroom_Programming": "#9e4eff",

            "Admin": "#bcbcbc",
            "Default": "#ff00aa"
        }

        self.clientURL = clientURL
        self.adminURL = adminURL
        self.submissionServerURL = submissionServerURL

    def GetQRCodeIconColorForName(self, name):
        if name in self.qrCodeIconColorDict:
            return self.qrCodeIconColorDict[name]

        return self.qrCodeIconColorDict["Default"]

    def GetQrCodeAssetPath(self):
        path = os.path.join(GetAssetDir(), "qrcodeIcons") 
        path = os.path.normpath(path)
        if not os.path.exists(path):
            os.mkdir(path)

        return path

    def GetQrCodeOutputPath(self):
        path = os.path.join(GetOutputDir(), "qrcodes")
        path = os.path.normpath(path)
        if not os.path.exists(path):
            os.mkdir(path)

        return path

    def GetIconWithName(self, name):
        path = os.path.join(self.GetQrCodeAssetPath(), name+".png")
        if os.path.exists(path):
            return path
        return None
        
    def GetDefaultIconPath(self):
        path = os.path.join(self.GetQrCodeAssetPath(), "Default.png")
        if os.path.exists(path):
            return os.path.normpath(path)
        return None

    def GenerateAllQrCodes(self):
        print(f"Generating QR Codes with:\nadminURL: {self.adminURL}\nclientURL: {self.clientURL}\nsubmissionURL: {self.submissionServerURL}")
        for code, boothName in GetBoothNameTable().items():
            data = f"{self.clientURL}/?c={code}"
            self.GenerateQrCode(boothName, data)

        data = f"{self.adminURL}/?c={GetAdminAccessCode()}"
        self.GenerateQrCode("Admin",data)

        data = f"{self.submissionServerURL}/?c={GetAdminAccessCode()}"
        self.GenerateQrCode("Submissions", data)

    def GetExistingQrCodes(self):
        qrCodeNames = os.listdir(self.GetQrCodeOutputPath())
        qrCodePaths = []
        for name in qrCodeNames:
            qrCodePath = os.path.join(self.GetQrCodeOutputPath(), name)
            qrCodePaths.append(os.path.normpath(qrCodePath))

        return qrCodePaths

    def RemovePreviousQrCodes(self):
        for qrCode in self.GetExistingQrCodes():
            if not os.path.isdir(qrCode):
                os.remove(qrCode)
        
    def GenerateQrCode(self,codeFileName, data):
        
        # Create a QR code object
        qr = qrcode.QRCode(
            version=2,  # controls the size of the QR Code (1 is the smallest)
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # controls error correction
            box_size=40,  # size of the box where QR code will be displayed
            border=4,  # border size around the QR code
        )

        # Add data to the QR code
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QR code
        qrCodeImg = qr.make_image(fill="black", back_color="white").convert("RGB")

        # Find and attach Icon
        iconPath = self.GetIconWithName(codeFileName)
        if not iconPath:
            iconPath = self.GetDefaultIconPath()

        if iconPath:
            qrCodeCenterIcon = Image.open(iconPath)
            borderSize = 40
            qrCodeCenterIcon = ImageOps.expand(qrCodeCenterIcon, border=borderSize, fill=self.GetQRCodeIconColorForName(codeFileName))
            qrWidth, qrHeight = qrCodeImg.size
            iconSize = qrWidth//4
            qrCodeCenterIcon = qrCodeCenterIcon.resize((iconSize, iconSize), Image.Resampling.LANCZOS)
            iconPos = ((qrWidth - iconSize)//2, (qrHeight - iconSize)//2)
            qrCodeImg.paste(qrCodeCenterIcon, iconPos, mask = qrCodeCenterIcon)

        # Save the image file
        qrCodeImg.save(os.path.join(self.GetQrCodeOutputPath(), codeFileName+".png"))

    def CombineQrCodesIntoPdf(self):
        qrCodePaths = self.GetExistingQrCodes()
        images = [Image.open(image) for image in qrCodePaths]
        images[0].save(os.path.join(self.GetQrCodeOutputPath(),'allQrCodes.pdf'), save_all=True, append_images=images[1:])

    def CombineQrCodeIntoImage(self, numOfColums = 3):
        qrCodePaths = self.GetExistingQrCodes()
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

        combinedImage.save(os.path.join(self.GetQrCodeOutputPath(), "allQrCodes.png"))


def main():
    # the url should be the url with port intergrated:
    # http://192.168.1.91:8501
    # if the port is intergrated with the url like the ones you would get from cloudflared tunneling,then only the tunneled url is requred.

    clientURL = GetURLFromUser("Client Server URL")
    adminURL = GetURLFromUser("admin Server URL")
    submissionURL = GetURLFromUser("submission Server URL")

    generator = QRCodeGen(clientURL, adminURL, submissionURL)
    generator.RemovePreviousQrCodes()
    generator.GenerateAllQrCodes()
    generator.CombineQrCodeIntoImage()


if __name__ == "__main__":
    main()