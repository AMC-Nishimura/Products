# Upload/consumers.py
import datetime
import io
import json
from logging import exception
import os
import sys
import threading
import time
from os.path import abspath, dirname, join
from textwrap import indent
from threading import Event, Thread
import asyncio

import cv2
import numpy as np
from channels.generic.websocket import (AsyncWebsocketConsumer)
from django.apps import apps as django_apps
from django.http import JsonResponse
from django.shortcuts import render
from PIL import Image
from Products.settings import BASE_DIR
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tabjudge.Candidate import Candidate
from tabjudge.Point import Point
from tabjudge.WsReturnData import WsReturnData
from tabjudge.ReturnDataEncoder import ReturnDataEncoder
from tabjudge.TabletData import TabletData



from .models import Image
from .serializer import ImageSerializer

import random
from PIL import Image


"""
WebsocketConsumer
"""
class UploadConsumer(AsyncWebsocketConsumer):
    
    rList = []
    lock = threading.Lock()


    async def connect(self):
        print("[connect] upgrade receive")
        self.rList = []
        self.st = datetime.datetime.today()
        self.rList.append('Connect Time = ' + self.st.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3] + '\n')

        print(vars(self))

        self.scope["session"]["seed"] = random.randint(1, 1000)
        #print(str(self.scope['cookies']['sessionid']))
        print('seed = ', str(self.scope['session']['seed']))
        
        # Websocketを受け取り、経路を作る
        await self.accept()
        
        dj = { 'message': 'msg' }
        await self.send(text_data=json.dumps(dj))
        
        #await self.SendData(json.dumps(dj))
        
        


    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # チャットの投稿を受け取り、それを返却する。
        print("text_data=" , text_data)
        message = text_data
        #text_data_json  = json.loads(text_data)
        #message         = text_data_json['message']

        await self.send(text_data=json.dumps({ 'message': "Anonymous > " + message }))
        #self.send(text_data=json.dumps({ 'message': "検閲済み" }))
        

    """
    Image Receive
    """
    async def receive(self, text_data=None, bytes_data=None):
        #send example 
        #inst = io.BytesIO(bytes_data)
        #img = Image.open(inst)
        #print(img.size)
        # await self.send(text_data=json.dumps({ 'image_size': str(img.size) }))
        print("receive")
        print('seed = ', str(self.scope['session']['seed']))

        self.st = datetime.datetime.today()
        self.rList.append('Receive Complete Time = ' + self.st.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3] + '\n')

        #print(vars(self))

        self.st = datetime.datetime.today()
        print("start time set")
        nparr = np.fromstring(bytes_data, np.uint8)
        print("bytes_data to numpy array complete")

        # #create session id
        # if not request.session.session_key:
        #     request.session.create()
        
        # #session available time.0=session delete when browser closing
        # request.session.set_expiry(0)
        # self.sessionId = request.session.session_key


        #self.sessionId = random.randint(1, 1000)
        self.sessionId = self.scope['session']['seed']
        #rList sessionID set
        self.rList.append('SessionID = ' + str(self.sessionId) + '\n')
                
        self.rList.append('doIdentifier Start Time = ' + self.st.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3] + '\n')

        await self.send(text_data=json.dumps({ 'image_size': 'identifier start' }))

        #identifier start
        self.doIdentifier(self.sessionId, nparr)

        #print("return")
        await self.send(text_data=json.dumps({ 'image_size': 'identifier end' }))

        return super().receive(text_data, bytes_data)




    def get_h_m_s(td):
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        return h, m, s


        #central.py do identifier
    def doIdentifier(self, sessionId, nparr):
        print("doIdentifier() sessionId = " , sessionId)
        app = django_apps.get_app_config('tabjudge')

        print("cv2 imdecode start")
        try:
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            print("cv2 imdecode complete")
            
            print("Central Identifier Start")
            app.Manager.Identifier(sessionId,
                                    img,
                                    self.CallBackSendResult,
                                    self.CallBackSendCompleted,
                                    self.LogWrite)
        except Exception as e:
            print(e)


    """
    
    """
    def CompleteIdentifier(self, sessionId):
        print('CMView.py completeIdentifier() start. sessionId = ', sessionId)

        app = django_apps.get_app_config('tabjudge')
        #CentralManager.py Complete()
        app.Manager.Complete(sessionId)
        
        #self.request.session.delete(sessionId)
        print("completeIdentifier finish")
        
        self.send("Complete")


        #コールバックさせる関数：結果セット関数
    def CallBackSendResult(self,
                            Contours,
                            CandidateList,
                            CropImage):
        print("CallBackSendResult")
        '''
        ここに鑑別結果を送信する処理を実装。
        今は仮でprintだけしておきます。
        '''
        
        self.lock.acquire()
        self.rList.append('')

        self.rList.append('1錠の鑑別結果コールバック')
        self.rList.append('日時 = '+datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3])
        self.rList.append('Contours:'+str(Contours.shape))
        self.rList.append('CropImage:'+str(CropImage.size))
        listcount = len(CandidateList)
        print('listCount =', listcount)
        for i in range(listcount):
            if(i >= 5):break
            ret = 'YJCode:'+str(CandidateList[i].YJCODE)
            ret += ',DNCode:'+str(CandidateList[i].FCODE)
            ret += ',SCORE:'+str(CandidateList[i].SCORE)
            self.rList.append(ret)


        self.rList.append('')
        #lock release
        self.lock.release()

        
        pointList = []  
        ContoursCount = len(Contours)
        for num in range(ContoursCount):
            pt = Point(Contours[num, 0], Contours[num, 1])
            pointList.append(pt)

        candiList = []
        listcount = len(CandidateList)
        for i in range(listcount):
            cd = Candidate(CandidateList[i].YJCODE,
                           CandidateList[i].FCODE,
                           str(CandidateList[i].NAME),
                           CandidateList[i].SCORE)
            candiList.append(cd)
        
        imgArray = np.array(CropImage)
        td = TabletData(pointList, candiList, imgArray)
        
        #self.recvTabDatas.append(td)
        print("data set")
        prms = {'indent':4,'ensure_ascii': False}
        rtData = WsReturnData(tbData = td, msg ='')

        print("complete set data")
        
        print("send to ...")
        try:
            #↓python3.7 から使える
            #asyncio.run(self.SendData("CallBackSendResult"))

            #asyncio.ensure_future(self.SendData("CallBackSendResult"))

       #     loop = asyncio.get_event_loop()
            #loop.run_until_complete(asyncio.wait(self.SendData("CallBackSendResult")))
            
        #    loop.run_until_complete(asyncio.wait(self.send(text_data=json.dumps(rtData, cls = ReturnDataEncoder, **prms))))

            #await self.send(text_data=json.dumps({ 'image_size': 'identifier start' }))
            #await self.send(text_data="CallBackSendResult")
            
            #print(str(vars(rtData)))
            #await self.SendData(json.dumps(rtData, cls = ReturnDataEncoder, **prms))
            
            
            #asyncio.ensure_future(self.SendData(json.dumps(rtData, cls = ReturnDataEncoder, **prms)))
            
            asyncio.ensure_future(self.send(text_data=json.dumps(rtData, cls = ReturnDataEncoder, **prms)))
            
            #self.run_until_complete(asyncio.wait(self.send(text_data=json.dumps(rtData, cls = ReturnDataEncoder, **prms))))
            
            #self.send(text_data=json.dumps(rtData, cls = ReturnDataEncoder, **prms))
            
            #self.SendData(json.dumps(rtData, cls = ReturnDataEncoder, **prms))
            
        except Exception as e:
            print(e)
        print("send completed")
        #self.send(text_data=json.dumps(rtData, cls = ReturnDataEncoder, **prms))
        #self.SendData("CallBackSendResult")
        #ret = '1錠の鑑別結果コールバック'+'\nContours:'+str(Contours.shape)+ '\nCandidateList:'+str(CandidateList)+ '\nCropImage:'+str(CropImage.size)
        #Dispose object
        del(Contours)
        del(CandidateList)
        del(CropImage)

    async def SendData(self, msg):
        try:
            await self.send(text_data=msg)
        except Exception as e:
            print(e)
        
        
    #コールバックさせる関数：ログ出力時に呼ぶ関数
    def LogWrite(self,strLog):
        self.lock.acquire()
        self.rList.append(str(datetime.datetime.today()) + ' @ ' + strLog)
        self.lock.release()

    #コールバックさせる関数：全ての鑑別が終わった際に呼ぶ関数
    def CallBackSendCompleted(self):

        '''
        ここに鑑別完了通知の送信など
        全ての鑑別が完了した際に行う処理を実装。
        今は仮でメッセージだけprintしておきます。
        '''
        
        #lock
        self.lock.acquire()
        
        # print('★全ての鑑別が終わりました★')
        self.rList.append('')
        self.rList.append('★全ての鑑別が終わりました(Rev:82)★')
        self.rList.append('日時 = '+datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3])
        self.rList.append('')
        
        #lock
        self.lock.release()
        
        self.CompleteIdentifier(self.sessionId)
        
        #print('Event set()')
        #self.event.set()
        



# class UploadConsumer(AsyncWebsocketConsumer):
    
#     rList = []
#     lock = threading.Lock()


#     async def connect(self):
#         print("[connect] upgrade receive")
        
#         self.rList = []
#         self.st = datetime.datetime.today()
#         self.rList.append('Connect Time = ' + self.st.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3] + '\n')

#         print(vars(self))

#         self.scope["session"]["seed"] = random.randint(1, 1000)
#         #print(str(self.scope['cookies']['sessionid']))
#         print('seed = ', str(self.scope['session']['seed']))
        
#         # Websocketを受け取り、経路を作る
#         await self.accept()
        
#         dj = { 'message': 'msg' }
#         #await self.send(text_data=json.dumps(dj))
        
#         await self.SendData(json.dumps(dj))
        
        


#     async def disconnect(self, close_code):
#         pass

#     async def receive(self, text_data):
#         # チャットの投稿を受け取り、それを返却する。
#         print("text_data=" , text_data)
#         message = text_data
#         #text_data_json  = json.loads(text_data)
#         #message         = text_data_json['message']

#         await self.send(text_data=json.dumps({ 'message': "Anonymous > " + message }))
#         #self.send(text_data=json.dumps({ 'message': "検閲済み" }))
        

#     """
#     Image Receive
#     """
#     async def receive(self, text_data=None, bytes_data=None):
#         #send example 
#         #inst = io.BytesIO(bytes_data)
#         #img = Image.open(inst)
#         #print(img.size)
#         # await self.send(text_data=json.dumps({ 'image_size': str(img.size) }))
#         print("receive")
#         print('seed = ', str(self.scope['session']['seed']))

#         self.st = datetime.datetime.today()
#         self.rList.append('Receive Complete Time = ' + self.st.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3] + '\n')

#         #print(vars(self))

#         self.st = datetime.datetime.today()
#         print("start time set")
#         nparr = np.fromstring(bytes_data, np.uint8)
#         print("bytes_data to numpy array complete")

#         # #create session id
#         # if not request.session.session_key:
#         #     request.session.create()
        
#         # #session available time.0=session delete when browser closing
#         # request.session.set_expiry(0)
#         # self.sessionId = request.session.session_key


#         #self.sessionId = random.randint(1, 1000)
#         self.sessionId = self.scope['session']['seed']
#         #rList sessionID set
#         self.rList.append('SessionID = ' + str(self.sessionId) + '\n')
                
#         self.rList.append('doIdentifier Start Time = ' + self.st.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3] + '\n')

#         await self.send(text_data=json.dumps({ 'image_size': 'identifier start' }))

#         #identifier start
#         self.doIdentifier(self.sessionId, nparr)

#         #print("return")
#         await self.send(text_data=json.dumps({ 'image_size': 'identifier end' }))

#         return await super().receive(text_data, bytes_data)




#     def get_h_m_s(td):
#         m, s = divmod(td.seconds, 60)
#         h, m = divmod(m, 60)
#         return h, m, s


#         #central.py do identifier
#     def doIdentifier(self, sessionId, nparr):
#         print("doIdentifier() sessionId = " , sessionId)
#         app = django_apps.get_app_config('tabjudge')

#         print("cv2 imdecode start")
#         try:
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#             print("cv2 imdecode complete")
            
#             print("Central Identifier Start")
#             app.Manager.Identifier(sessionId,
#                                     img,
#                                     self.CallBackSendResult,
#                                     self.CallBackSendCompleted,
#                                     self.LogWrite)
#         except Exception as e:
#             print(e)


#     """
    
#     """
#     async def CompleteIdentifier(self, sessionId):
#         print('CMView.py completeIdentifier() start. sessionId = ', sessionId)

#         app = django_apps.get_app_config('tabjudge')
#         #CentralManager.py Complete()
#         app.Manager.Complete(sessionId)
        
#         #self.request.session.delete(sessionId)
#         print("completeIdentifier finish")
        
#         self.send("Complete")


#         #コールバックさせる関数：結果セット関数
#     def CallBackSendResult(self,
#                             Contours,
#                             CandidateList,
#                             CropImage):
#         print("CallBackSendResult")
#         '''
#         ここに鑑別結果を送信する処理を実装。
#         今は仮でprintだけしておきます。
#         '''
        
#         self.lock.acquire()
#         self.rList.append('')

#         self.rList.append('1錠の鑑別結果コールバック')
#         self.rList.append('日時 = '+datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3])
#         self.rList.append('Contours:'+str(Contours.shape))
#         self.rList.append('CropImage:'+str(CropImage.size))
#         listcount = len(CandidateList)
#         print('listCount =', listcount)
#         for i in range(listcount):
#             if(i >= 5):break
#             ret = 'YJCode:'+str(CandidateList[i].YJCODE)
#             ret += ',DNCode:'+str(CandidateList[i].FCODE)
#             ret += ',SCORE:'+str(CandidateList[i].SCORE)
#             self.rList.append(ret)


#         self.rList.append('')
#         #lock release
#         self.lock.release()

        
#         pointList = []  
#         ContoursCount = len(Contours)
#         for num in range(ContoursCount):
#             pt = Point(Contours[num, 0], Contours[num, 1])
#             pointList.append(pt)

#         candiList = []
#         listcount = len(CandidateList)
#         for i in range(listcount):
#             cd = Candidate(CandidateList[i].YJCODE,
#                            CandidateList[i].FCODE,
#                            str(CandidateList[i].NAME),
#                            CandidateList[i].SCORE)
#             candiList.append(cd)
        
#         imgArray = np.array(CropImage)
#         td = TabletData(pointList, candiList, imgArray)
        
#         #self.recvTabDatas.append(td)
#         print("data set")
#         prms = {'indent':4,'ensure_ascii': False}
#         rtData = ReturnData(tbData = td, msg ='')

#         print("complete set data")
        
#         print("send to ...")
        
#         #↓python3.7 から使える
#         #asyncio.run(self.SendData("CallBackSendResult"))

#         #asyncio.ensure_future(self.SendData("CallBackSendResult"))

#         #loop = asyncio.get_event_loop()        
#         #loop.run_until_complete(asyncio.wait(self.SendData("CallBackSendResult")))


#         #await self.send(text_data="CallBackSendResult")
        
#         #print(str(vars(rtData)))
#         #await self.SendData(json.dumps(rtData, cls = ReturnDataEncoder, **prms))
#         asyncio.ensure_future(self.SendData(json.dumps(rtData, cls = ReturnDataEncoder, **prms)))
        
#         print("send completed")
#         #self.send(text_data=json.dumps(rtData, cls = ReturnDataEncoder, **prms))
#         #self.SendData("CallBackSendResult")
#         #ret = '1錠の鑑別結果コールバック'+'\nContours:'+str(Contours.shape)+ '\nCandidateList:'+str(CandidateList)+ '\nCropImage:'+str(CropImage.size)
#         #Dispose object
#         del(Contours)
#         del(CandidateList)
#         del(CropImage)

#     async def SendData(self, msg):
#         await self.send(text_data=msg)
        
        
#     #コールバックさせる関数：ログ出力時に呼ぶ関数
#     def LogWrite(self,strLog):
#         self.lock.acquire()
#         self.rList.append(str(datetime.datetime.today()) + ' @ ' + strLog)
#         self.lock.release()

#     #コールバックさせる関数：全ての鑑別が終わった際に呼ぶ関数
#     def CallBackSendCompleted(self):

#         '''
#         ここに鑑別完了通知の送信など
#         全ての鑑別が完了した際に行う処理を実装。
#         今は仮でメッセージだけprintしておきます。
#         '''
        
#         #lock
#         self.lock.acquire()
        
#         # print('★全ての鑑別が終わりました★')
#         self.rList.append('')
#         self.rList.append('★全ての鑑別が終わりました(Rev:82)★')
#         self.rList.append('日時 = '+datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3])
#         self.rList.append('')
        
#         #lock
#         self.lock.release()
        
#         self.CompleteIdentifier(self.sessionId)
        
#         #print('Event set()')
#         #self.event.set()
        
        
        

