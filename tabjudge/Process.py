import cv2
import numpy as np
import threading
import random
import numpy as np

class Process():

    def __init__(self,SegModelPath,MasterPath):
        super(Process,self).__init__()
        self.model = None #本来は 「load_model(SegModelPath)」 的なことをする
        self.master = None #本来は 「load_master(MasterPath)」 的なことをする
        self.master_list = [i for i in range(100)]
        self.master_thread_num = 5

    def DetectDrugRegion(self,img):
        #薬品領域を見つける処理を実装（下記は仮)

        mask = np.zeros(img.shape[:2])
        mask[10:20,10:20] = 255
        mask[30:45,50:65] = 255
        mask[50:75,80:100] = 255

        return mask.astype('uint8')

    def SplitDrugRegion(self,mask):
        #領域を1錠ずつに切り分ける処理を実装（下記は仮)
        contours,hierarchy = cv2.findContours(mask, 1, 2)
        return contours

    def ExtractEmboss(self,img,contour):
        #刻印を抽出する処理を実装(下記は仮)
        mask = np.zeros(img.shape).astype('uint8')
        x,y,w,h = cv2.boundingRect(contour)
        img = img[y:y+h,x:x+w]
        mask = mask[y:y+h,x:x+w]
        img[mask == 0] = 0
        mask[:,5:10] = 255
        return mask

    def Matching(self,emboss):
        #マスタとのマッチング処理をマルチスレッドで実行し、
        #終了を待ち合わせて結果を返す（下記は仮）
        thread_list = []
        split_masters = [[] for i in range(self.master_thread_num)]
        for i in range(len(self.master_list)):
            split_masters[i%self.master_thread_num].append(
                {'master':self.master_list[i],
                 'score':None})
        for num in range(self.master_thread_num):
            thread = threading.Thread(
                target = self._SingleProcessMatching,
                args = [emboss,split_masters[num]])
            thread_list.append(thread)
            thread.start()
        for t in thread_list:
            t.join()
        results = []
        for masters in split_masters:
            results += masters
        #print(results)
        results = sorted(results,key = lambda x:x['score'],reverse=True)
        return results

    def _SingleProcessMatching(self,emboss,masters):
        #マスタとのマッチング処理を実装する（下記は仮）
        for master in masters:
            score = self.CalcuMatchScore(emboss,master)
            master['score'] = score
            
    def CalcuMatchScore(self,img,master):
        #1対1のマッチング処理スコアを返す（下記は仮）
        score = random.randint(0,1000)/1000
        return score
