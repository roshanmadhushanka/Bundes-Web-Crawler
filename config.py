import cPickle as pickle
import os.path

from flask import session

prop = {
    'PROCEED' : True,
    'SLEEP_TIME': 10,
    'SAVE_INTERVAL': 10,
    'LINK_LIST_PATH': 'link_list',
    'COMPANY_LIST_PATH': 'company_list'
}


def saveConfig():
    global prop
    with open('config', 'wb') as fp:
        pickle.dump(prop, fp)


def loadConfig():
    global prop
    if os.path.exists('config'):
        with open('config', 'rb') as fp:
            prop = pickle.load(fp)
            session['company_list_path'] = prop['COMPANY_LIST_PATH']
            session['link_list_path'] = prop['LINK_LIST_PATH']
            session['save_interval'] = prop['SAVE_INTERVAL']
            session['sleep_time'] = prop['SLEEP_TIME']
            session['proceed'] = prop['PROCEED']



