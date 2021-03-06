from .Central import Central
import os

class CentralManager():
    CentralDictionary = {}
    
    def __init__(self):
        iniCen = Central()
        self.DrugInfModule = iniCen.Initialize('./setting.ini')

    def Identifier(self,
                    SessionId,
                    ImgInput,
                    cbSendResult,
                    cbSendCompleted,
                    cbLogWrite):

        cen = Central()
        self.CentralDictionary[SessionId] = cen
        self.CentralDictionary[SessionId].Identifier(self.DrugInfModule,
                                                    ImgInput,
                                                    cbSendResult,
                                                    cbSendCompleted,
                                                    cbLogWrite)
        del cen
        #del self.CentralDictionary[SessionId]
    
    def Complete(self,
                SessionId):
        if SessionId in self.CentralDictionary.keys():
            print('CentralManager.py Complete()')
            #print('CentralManager.py Complete() Centrl = ', vars(self.CentralDictionary[SessionId]))
            
            #Dispose() = Centray.py dispose()
            self.CentralDictionary[SessionId].Dispose()
            #remove sessionId
            self.CentralDictionary.pop(SessionId)
