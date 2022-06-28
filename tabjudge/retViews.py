#coding: UTF-8
import json
from textwrap import indent
from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
import os
from rest_framework.response import Response
from threading import (Event, Thread)
from tabjudge.ReturnData import ReturnData
from tabjudge.ReturnDataEncoder import ReturnDataEncoder
from tabjudge.Candidate import Candidate

from tabjudge.TabletData import TabletData
from tabjudge.Point import Point 

from .models import Image
from .serializer import ImageSerializer
import cv2
import datetime
import time
import numpy as np
import sys

from os.path import abspath, join, dirname
from django.apps import apps as django_apps
from Products.settings import BASE_DIR

from django.http import JsonResponse
from rest_framework import status

UPLOAD_DIR = 'static/uploaded_photo/'
DOWNLOAD_DIR = 'static/download_photo/'

class UploadViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    
    rList = []
    sessionId = ''


    # カスタムエンドポイントを作成する場合は@actionを使用
    #@action(detail=true, methods=)
    def create(self, request):
        
        #add starttime
        start_time = time.perf_counter()
        self.st = datetime.datetime.today()
        
        file = request.FILES['file']
        print('file dump = ', vars(file))

        #first step
        file_data = file.read()

        nparr = np.fromstring(file_data, np.uint8)

        path = os.path.join(os.path.join(BASE_DIR, UPLOAD_DIR), file.name)


        destination = open(path, 'wb')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()

        if not os.path.exists(path):
            print('File not found:', path)
            return create_render(request)
        
        self.rList = []
        self.event = Event()

        #rList sessionID set
        self.rList.append('Start Time = ' + self.st.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3] + '\n')

        #create session id
        if not request.session.session_key:
            request.session.create()
        
        #session available time.0=session delete when browser closing
        request.session.set_expiry(0)
        self.sessionId = request.session.session_key

        #rList sessionID set
        self.rList.append('SessionID = ' + str(self.sessionId) + '\n')
        
        #identifier start
        self.doIdentifier(self.sessionId, nparr)
        
        print("Event wait()")
        self.event.wait()
        self.event.clear()
        
        print("identifier end")
        
        self.ed = datetime.datetime.today()
        self.rList.append('End Time = ' + self.ed.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3] + '\n')

        execution_time = self.ed - self.st
        self.rList.append('\nTime Span (時:分:秒.ミリ秒) = ' + str(execution_time)[:-3])

        #print('param = {', '\n'.join(self.rList) , '}')
        print("render")
        
        msg = ('\n'.join(self.rList) )
        
        tabletDatas = []
        candiList = []
        
        cdyj = [["1149019F1242","1149019F1560","1149019F1579"],
                ["1124001F1022","1124001F2029","1124001B1039"],
                ["1124003F2265","1124003F2273","1124003F2290"]
                ]
        cdf = [["FCODE000001","FCODE000002", "FCODE000003"],
               ["FCODE010001","FCODE010002", "FCODE010003"],
               ["FCODE020001","FCODE020002", "FCODE020003"]
               ]
        cdnm = [["ロキフェン錠60mg","ロキソニン錠60mg","ロキソプロフェンナトリウム錠60mg「クニヒロ」"],
                ["ユーロジン1mg錠","ユーロジン2mg錠","ユーロジン散1%"],
                ["ニトラゼパム錠5mg「JG」","ニトラゼパム錠5mg「ツルハラ」","ニトラゼパム錠5mg「テバ」"]
                ]
        
        tbnm = ["TrimBmp001.jpg", "TrimBmp002.jpg", "TrimBmp003.jpg"]
        
        for i in range(3):
            pointList = []
            for num in range(5):
                pt = Point(i, i * 100 + num)
                pointList.append(pt)
                
            candiList = []
            for cdNum in range(3):
                cd = Candidate(cdyj[i][cdNum]
                               , cdf[i][cdNum]
                               , cdnm[i][cdNum]
                               , i * 100 + cdNum)
                candiList.append(cd)
            
            trimBmpPath = os.path.join(os.path.join(BASE_DIR, DOWNLOAD_DIR), tbnm[i])
            print("bmpPath = ",trimBmpPath)
            td = TabletData(pointList, candiList, trimBmpPath)
            tabletDatas.append(td)

        rtData = ReturnData(tabletDatas, msg)
        #print(vars(rtData.tabletDatas))
        
        print('msg =',msg)
        
        #enc_data = json.dumps(rtData, cls= ReturnDataEncoder, indent=4, ensure_ascii=False)
        #print(enc_data)
        

        # return JsonResponse(enc_data,
        #                      safe=False,
        #                      status= status.HTTP_200_OK,
        #                      json_dumps_params={'ensure_ascii': False}
        #                      )


        return JsonResponse(rtData,
                            safe=False,
                            status= status.HTTP_200_OK,
                            encoder=ReturnDataEncoder,
                            json_dumps_params={'indent':4,'ensure_ascii': False}
                            )


    def get_h_m_s(td):
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        return h, m, s


        #central.py do identifier
    def doIdentifier(self, sessionId, nparr):
        print("doIdentifier()" , sessionId)
        app = django_apps.get_app_config('tabjudge')
        #imgPath = abspath( join(dirname(__file__),'IMG_4869.JPG') )
        #print("imgPath" , imgPath)
        #img = cv2.imread('./IMG_4869.JPG')
        #img = cv2.imread(imgPath)

        print("cv2 imdecode start")
        try:
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            #pt = os.path.join(os.path.join(BASE_DIR, UPLOAD_DIR),'IMG_4869.JPG')
            # print('img path = ', pt)
            # img = cv2.imread(pt)
            

            print("sessionId = ", sessionId)
            app.Manager.Identifier(sessionId,
                                    img,
                                    self.CallBackSendResult,
                                    self.CallBackSendCompleted)
        except Exception as e:
            print(e)


    def CompleteIdentifier(self, sessionId):
        print('CMView.py completeIdentifier() start. sessionId = ', sessionId)

        app = django_apps.get_app_config('tabjudge')
        #CentralManager.py Complete()
        app.Manager.Complete(sessionId)
        
        #self.request.session.delete(sessionId)
        print("completeIdentifier finish")



        #コールバックさせる関数：結果セット関数
    def CallBackSendResult(self,
                            Contours,
                            CandidateList,
                            CropImage):

        '''
        ここに鑑別結果を送信する処理を実装。
        今は仮でprintだけしておきます。
        '''
        self.rList.append('1錠の鑑別結果コールバック')
        self.rList.append('日時 = '+datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3])
        self.rList.append('Contours:'+str(Contours.shape))
        self.rList.append('CropImage:'+str(CropImage.size))
        listcount = len(CandidateList)
        for i in range(listcount):
            if(i >= 5):break
            ret = 'YJCode:'+str(CandidateList[i].YJCODE)
            ret += ',DNCode:'+str(CandidateList[i].FCODE)
            ret += ',SCORE:'+str(CandidateList[i].SCORE)
            self.rList.append(ret)
        #ret = '1錠の鑑別結果コールバック'+'\nContours:'+str(Contours.shape)+ '\nCandidateList:'+str(CandidateList)+ '\nCropImage:'+str(CropImage.size)
        #Dispose object
        del(Contours)
        del(CandidateList)
        del(CropImage)
        

    #コールバックさせる関数：全ての鑑別が終わった際に呼ぶ関数
    def CallBackSendCompleted(self):

        '''
        ここに鑑別完了通知の送信など
        全ての鑑別が完了した際に行う処理を実装。
        今は仮でメッセージだけprintしておきます。
        '''

        # print('★全ての鑑別が終わりました★')
        self.rList.append('★全ての鑑別が終わりました(Rev:82)★')
        self.rList.append('日時 = '+datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3])
        
        self.CompleteIdentifier(self.sessionId)
        
        print('Event set()')
        self.event.set()

