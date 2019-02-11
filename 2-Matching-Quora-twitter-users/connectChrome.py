
# -*- coding: utf-8 -*-
import pickle
import sys
sys.path

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from pprint import pprint
 
from bs4 import BeautifulSoup
import bs4
import time
import os
import re
DEBUG = 1
import mechanicalsoup
import urllib.request 
import requests
import traceback
#from cookielib import cookiejar
from selenium import webdriver
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy


def connectchrome():
    raw_answers = []
    count = 0
  
    loaded_answers = []
    title_list = []
    upvote_list = [] 
    options = Options()
    options.add_argument('--headless')
    options.add_argument('log-level=3')
    options.add_argument("--incognito")
    driver = webdriver.Chrome(chrome_options=options)
    driver.execute_script('window.scrollTo(0, 0);')
    chromedriver = "/home/youcef/Documents/quora/twitter-matching-accounts/chromedriver"   # Needed?
    os.environ["webdriver.chrome.driver"] = chromedriver     
    browser = webdriver.Chrome(chrome_options=options) 
    #browser.get('https://www.quora.com/')
    time.sleep(2)
    return browser  
    
