#
# Gunicorn config file
#
wsgi_app = 'Products.asgi:application'

# Server Mechanics
#========================================
# current directory
chdir = '/home/user/yuyama/Products'

# daemon mode
daemon = False

# enviroment variables
raw_env = [
    'ENV_TYPE=dev',
    'HOGEHOGE_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx'
]

timeout = 180

# Server Socket
#========================================
bind = '0.0.0.0:8001'

# Worker Processes
#========================================
workers =1

worker_class = "uvicorn.workers.UvicornWorker"

threads = 4


#  Logging
#========================================
# access log
accesslog = 'access.log'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# gunicorn log
errorlog = '-'
loglevel = 'info'
