from django.apps import AppConfig
from .Central import Central
from .CentralManager import CentralManager

import os

class TabjudgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tabjudge'

    def ready(self):
        print("curent =", os.getcwd())
        print("application be initialized")
        #Initialize
        self.Manager = CentralManager()
