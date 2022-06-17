import threading
import cv2
from .Process import Process
import configparser
import numpy as np

class Central():

    def __init__(self):
        pass
    

    '''
    ・初期化時に1度だけ呼ばれる
    ・メインの鑑別モジュールクラスをインスタンス化、初期化し、
    　インスタンスそのものを戻り値として返す。
    '''
    def Initialize(self,SettingIniPath):
        param_ini = configparser.ConfigParser()
        param_ini.read(SettingIniPath,encoding='utf-8')
        ret = Process(param_ini['PARAM']['SEG_MODEL_PATH'],
                      param_ini['PARAM']['MASTER_PATH'])
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
        if True:
            #① 入力画像から薬品部分の領域を取得
            #② for 領域 in 検出した領域群:
            #    ③ 刻印の抽出
            #    ④ マスタとのマッチング（内部はマルチスレッド）
            #    ⑤ 1錠の鑑別結果返却コールバック関数を呼び出し
            #⑥ 1枚画像の鑑別が完了したことを通知するコールバック関数を呼び出し

            mask = MainJudgeModule.DetectDrugRegion(ImgInput)
            contours = MainJudgeModule.SplitDrugRegion(mask)

            for contour in contours:
                emboss = MainJudgeModule.ExtractEmboss(ImgInput,contour)
                results = MainJudgeModule.Matching(emboss)

                DrugPoint = np.array([150,450])
                Area = 6400
                CandidateList = ['A','B','C']
                CropImage = ImgInput[0:32,0:32,:]
                StampImage = np.zeros([32,32])
                PrintImage = None

                cbSendResult(
                    DrugPoint,
                    Area,
                    CandidateList,
                    CropImage,
                    StampImage,
                    PrintImage)
            cbSendCompleted()
            
            return 0
        #except:
        #    print('落ちました')
        #    return -1

    def Cancel(self):
        pass
    
    def Dispose(self):
        print("Central.py dispose()")
        
