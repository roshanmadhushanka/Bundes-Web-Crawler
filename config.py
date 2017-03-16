import os.path
import sys

PROCEED = True
SLEEP_TIME = 10
SAVE_INTERVAL = 1
LINK_LIST_PATH = 'link_list'
COMPANY_LIST_PATH = 'company_list'
HOST = '127.0.0.1'
PORT = 5008

HOME = os.getcwd()

os_version = sys.platform.lower()
GECKODRIVER_PATH = ''
RESULT_OUT_PATH = ''
DATABASE_PATH = ''
if os_version.startswith('linux'):
    GECKODRIVER_PATH = HOME + '/driver/geckodriver'
    RESULT_OUT_PATH = HOME + '/result/'
    DATABASE_PATH = HOME + '/database/'
elif os_version.startswith('win'):
    GECKODRIVER_PATH = HOME + '\driver\geckodriver.exe'
    RESULT_OUT_PATH = HOME + '\\result\\'
    DATABASE_PATH = HOME + '\\database\\'






