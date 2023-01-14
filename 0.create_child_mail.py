# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from selenium.webdriver.chrome.service import Service as ChromeService, Service
from webdriver_manager.chrome import ChromeDriverManager
from configuration import config
from datetime import datetime
from time import sleep
import random
import os
import pickle

mailprefix='pre'
mailsuffix="@pokemail.net"
mailpwd='zxcvbnm123'

def create_account():
    root = 'ExtraFiles//0-reg-mail/'
    for fl in os.listdir(root):
        flpath = os.path.join(root, fl)
        mailprefix=flpath[flpath.find("_")+1:flpath.find(".txt")]
        f = open("ExtraFiles//1-reg-presearch//"+fl, "a+")
        account_index = 1
        while account_index<=40:
            sleep(1)
            account_index_2='%02d' % account_index
            account=mailprefix+str(account_index_2)
            f.write("{}{}:{}\n".format(account,mailsuffix, mailpwd))
            account_index+=1
        f.close()
        os.remove(flpath)

create_account()
