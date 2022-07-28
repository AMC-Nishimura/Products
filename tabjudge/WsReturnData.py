

class WsReturnData:
    
    #status 0:processing 1:complete
    def __init__(self, status, tbData, msg):
        self.status = status
        self.tabletData = tbData
        self.message = msg
