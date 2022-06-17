from .Central import Central
import os
from os.path import abspath, join, dirname

class CentralManager():
    CentralDictionary = {}
    
    def __init__(self):
        iniCen = Central()
        #add alpha
        iniPath = abspath( join(dirname(__file__),'setting.ini') )
        print(iniPath)
        #self.DrugInfModule = iniCen.Initialize('./setting.ini')
        self.DrugInfModule = iniCen.Initialize(iniPath)

    def Identifier(self,
                    SessionId,
                    ImgInput,
                    cbSendResult,
                    cbSendCompleted):

        cen = Central()
        self.CentralDictionary[SessionId] = cen
        self.CentralDictionary[SessionId].Identifier(self.DrugInfModule,
                                                    ImgInput,
                                                    cbSendResult,
                                                    cbSendCompleted)
    
    def Complete(self,
                SessionId):
        if SessionId in self.CentralDictionary.keys():
            print('CentralManager.py Complete()')
            #print('CentralManager.py Complete() Centrl = ', vars(self.CentralDictionary[SessionId]))
            
            #Dispose() = Centray.py dispose()
            self.CentralDictionary[SessionId].Dispose()
            #remove sessionId
            self.CentralDictionary.pop(SessionId)
