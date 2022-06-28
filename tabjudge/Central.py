from .Process import Process
import configparser
import numpy as np
import time
from PIL import Image

class Central():

    def __init__(self):
        pass
    

    '''
    ・初期化時に1度だけ呼ばれる
    ・メインの鑑別モジュールクラスをインスタンス化、初期化し、
    　インスタンスそのものを戻り値として返す。
    '''
    def Initialize(self,SettingIniPath):
        #imgproc.ReadMaster()
        param_ini = configparser.ConfigParser()
        param_ini.read(SettingIniPath,encoding='utf-8')
        ret = Process(param_ini['PARAM']['SEG_MODEL_PATH'],
                      param_ini['PARAM']['MASTER_PATH'],
                      param_ini['PARAM']['SETTING_CPP_PATH'])
        
        return ret

    '''
    ・鑑別のリクエスト1回につき1度呼ばれる（繰り返し呼ばれる）
    ・初期化済み鑑別モジュールインスタンスを直接引数で受け取り
    　モジュールの処理を呼び出して鑑別を行う。
    '''
    def Identifier(self,
                   MainJudgeModule,
                   ImgInput,
                   cbSendResult,
                   cbSendCompleted):
        # [GET_TAB_REGION]
        # Make Image bufffer fot C++
        tInitGetTab = time.time()
        IdnetifierObj = MainJudgeModule.GetTabRegion(ImgInput)
        print('[GetTabRegion] ' + str(IdnetifierObj.DrugCount) + ' object(s)')
        print('[GetTabRegion] ' + str(time.time() - tInitGetTab) + ' [s]')

        # [IDENTIFIER]
        # for i in range(IdnetifierObj.DrugCount):
        for i in range(IdnetifierObj.DrugCount):
            result = MainJudgeModule.Identifier_Proc(i, IdnetifierObj)
            contoursX = result.ContoursX
            contoursY = result.ContoursY
            CandidateList = result.ScoreList
    
            array_gbr = result.CropppedDrugImage.copy()
            array_rgb = result.CropppedDrugImage.copy()
            array_rgb[:, :, 0], array_rgb[:, :, 2] = array_gbr[:, :, 2], array_gbr[:, :, 0]
            CropImage = Image.fromarray(array_rgb)
    
            drogpoints = [[x,y] for x,y in zip(contoursX, contoursY)]
            Contours = np.array(drogpoints)
            cbSendResult(Contours, CandidateList, CropImage)
            del result
        cbSendCompleted()
        del IdnetifierObj
        return 0

    def Cancel(self):
        pass
    
    def Dispose(self):
        print("Central.py dispose()")
        
