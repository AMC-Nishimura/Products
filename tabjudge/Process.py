from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

import imgproc
import os
from Products.settings import BASE_DIR

class Process():

    def __init__(self,SegModelPath,MasterPath,SettingCppPath):
        super(Process,self).__init__()
        #print(os.path.join(BASE_DIR,SettingCppPath))
        #imgproc.Initialize(os.path.join(BASE_DIR,SettingCppPath))
        imgproc.Initialize(SettingCppPath)

    def GetTabRegion(self,img_gbr):
        IdnetifierObj = imgproc.GetTabRegionPy(img_gbr)
        return IdnetifierObj

    def Identifier_Proc(self,i,IdnetifierObj):
        result = imgproc.IdentifierPy(i, IdnetifierObj)
        return result
