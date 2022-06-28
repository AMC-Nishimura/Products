#coding: UTF-8
from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
import os
from rest_framework.response import Response
from threading import (Event, Thread)

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

UPLOAD_DIR = 'static/uploaded_photo/'

class ImageViewSet(viewsets.ModelViewSet):
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
        		
        #print('file_data[0] = ', file_data[0])
        #print('file_data[1] = ', file_data[1])
        #print('file_data[2] = ', file_data[2])
        #print('file_data[3] = ', file_data[3])
        #print('file_data[4] = ', file_data[4])

        nparr = np.fromstring(file_data, np.uint8)
        #img = cv2.imdecode(nparr, flags = cv2.IMREAD_COLOR)



        #print('nparr dump = ', vars(nparr))

        #print('nparr[0] = ', nparr[0])
        #print('nparr[1] = ', nparr[1])
        #print('nparr[2] = ', nparr[2])
        #print('nparr[3] = ', nparr[3])
        #print('nparr[4] = ', nparr[4])

        #img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        #file = request.FILES['file']
        path = os.path.join(os.path.join(BASE_DIR, UPLOAD_DIR), file.name)


        destination = open(path, 'wb')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()

        if not os.path.exists(path):
            print('File not found:', path)
            return create_render(request)
        
        # image, created = Image.objects.get_or_create(filepath=path)
        # if created:
        #     # image.sender = request.POST['sender']
        #     image.title = request.POST['title']
        #     image.body = request.POST['body']
        #     image.created_at = request.POST['created_at']
        #     image.updated_at = request.POST['updated_at']
        #     image.lat = float(request.POST['lat'])
        #     image.lng = float(request.POST['lng'])
        #     image.status = request.POST['status']
        #     #image.save()
        
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
        
        #execution time
        #execution_time = time.perf_counter() - start_time
        
        # self.rList.append('\nTime Span (分:秒.ミリ秒) = ' + datetime.datetime.fromtimestamp(execution_time ).strftime('%M:%S.%f'))
        
        #print(execution_time)
        
        #h, m, s = self.get_h_m_s(execution_time)
        #ms = execution_time.microseconds / 1000
        self.ed = datetime.datetime.today()
        self.rList.append('End Time = ' + self.ed.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3] + '\n')

        execution_time = self.ed - self.st
        self.rList.append('\nTime Span (時:分:秒.ミリ秒) = ' + str(execution_time)[:-3])

        print('param = {', '\n'.join(self.rList) , '}')
        #params = {"message":'\n'.join(self.rList)}
        print("render")
        
        #msg = ('result'+'param = {', '\n'.join(self.rList) , '}')
        msg = ('\n'.join(self.rList) )
        
        return Response({'message': msg})
        #return Response({'message': 'OK'})

    def retrieve(self, request, *args, **kwargs):
        
        
        
        return Response({
            
            
            
            
        })



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
