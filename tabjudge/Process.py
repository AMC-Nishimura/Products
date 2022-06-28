import imgproc

class Process():

    def __init__(self,SegModelPath,MasterPath,SettingCppPath):
        super(Process,self).__init__()
        imgproc.Initialize(SettingCppPath)

    def GetTabRegion(self,img_gbr):
        IdnetifierObj = imgproc.GetTabRegionPy(img_gbr)
        return IdnetifierObj

    def Identifier_Proc(self,i,IdnetifierObj):
        result = imgproc.IdentifierPy(i, IdnetifierObj)
        return result
