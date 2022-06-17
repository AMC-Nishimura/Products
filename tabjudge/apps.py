from django.apps import AppConfig
from .Central import Central
from .CentralManager import CentralManager

class TabjudgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tabjudge'

    def ready(self):
        print("application be initialized")
        #Initialize
        self.Manager = CentralManager()
