import json
from tabjudge.ReturnData import ReturnData

from tabjudge.TabletData import TabletData
from . import Point
import uuid
import numpy

class ReturnDataEncoder(json.JSONEncoder):
    def default(self, obj):
        # if isinstance(obj, TabletData):
        #     return {'data':obj.data}
        # elif isinstance(obj, ReturnData):
        #     return {'tableDatas':obj.tabletDatas, 'message':obj.message}
        if isinstance(obj, object) and hasattr(obj, '__dict__'):
            return obj.__dict__
        elif isinstance(obj, numpy.integer):
            return int(obj)
        #elsif isinstance(obj, object) and hasattr(obj, '__dict__'):
        #    return obj.__dict__
        #return super(ReturnDataEncoder, self).default(obj)
        return super().default(obj)
     