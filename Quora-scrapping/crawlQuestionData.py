# -*- coding: utf-8 -*-
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
from bs4 import BeautifulSoup
import bs4
import time
import os
import re
DEBUG = 1
from datetime import datetime, timedelta
import dateparser
import calendar
from connectChrome import connectchrome


def convertnumber(number):
    if 'k' in number:
        n=float(number.replace('k', '').replace(' ', ''))*1000
    elif 'm' in number:
        n=float(number.replace('m', '').replace(' ', ''))*1000000
    else:
        n=number
    return int(n)   


def scrolldown(browser):        
    src_updated = browser.page_source
    src = ""
    while  src != src_updated:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        src = src_updated
        src_updated = browser.page_source      
       

def crawlQuestionData(file):
    start_time = time.time()
    #if (DEBUG): #print ("In crawlQuestionData...")
    # Open question url file
    file_question_urls = open(file, mode = 'r')
    #file_answers = open(os.path.join(sys.path[0]+"zzanswers.txt", mode = 'ab'))
    file_answers = open("/home/youcef/Documents/quora/quora-answers-profiles-scraper/zzanswers,txt", mode = 'ab')

    #file_users = open(os.path.join(sys.path[0]+"users.txt", mode = 'a'))
    current_lines = file_question_urls.readlines()
    i=-1
    browser= connectchrome()
    k=0
    loop=True
    #for current_line in current_lines:
    while  loop :
        current_line= current_lines[k]
        print('processing question number  : '+ str(k))
        k+=1
        if '/unanswered/' in str(current_line):
            print('answer is unanswered')
            continue     
        print ("*************************************************************************")
        if (DEBUG): print(current_line)
        question_id = current_line
        browser.get(current_line)
        #if (DEBUG): #print ("got current line...")
        time.sleep(0.5)
        scrolldown(browser)       
        html_source = browser.page_source
        soup = BeautifulSoup(html_source,"html.parser")
        
        # initiate browser 
        browser.maximize_window()
        wait = WebDriverWait(browser, 40)
        
        # QUESTION id
        question_id = current_line.rsplit('/', 1)[-1] 
        question_id = question_id[:-1]
       
        
        # find title 
        title= soup.findAll("span", {"class": "ui_story_title ui_story_title_large "})
       
        # find question topics
        questions_topics= soup.findAll("span", {"class": "TopicName"})
        questions_topics_text=[]
        for topic in questions_topics : questions_topics_text.append(topic.text)
        print(questions_topics_text)
 
        
        # number of answers 
        # not all answers are saved!
        # answers that collapsed, and those written by annonymous users are not saved
        try:
            nbquestions = soup.find("div", {"class": "answer_count"})
            nb= [int(s) for s in nbquestions.text.split() if s.isdigit()][0]
            print("number of answers is    "+str(nb))
            if nb>7: # if there is more than 8 answers than we have to scrolldown to load remaining ones
                scrolldown(browser)
            html_source = browser.page_source
            soup = BeautifulSoup(html_source,"html.parser")   
            # Split html to parts
            split_html = html_source.split('class="Answer AnswerBase')            
        except Exception as notexist :#mostly because question is deleted by quora
            print('question no long exists')
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(notexist).__name__, notexist)
            print(str(notexist))
            continue    
            
        for i in range(1, len(split_html)):
            try:  
               part = split_html[i]
               part_soup = BeautifulSoup(part,"html.parser" )
               print('=====================')   
                        
               #find users names of answers authors
               authors=  part_soup.find("a", {"class": "user"}, href=True)
               
               #print(authors)
               user_id = (authors['href']).rsplit('/', 1)[-1]
               print(user_id)
                                            
               # find answer dates
               answer_date= part_soup.find("a", {"class": "answer_permalink"})
               date=answer_date.text
                
               if ("Updated" in date):
                   date= date[8:]
               else:
                   date= date[9:]
               
               date=dateparser.parse(date).strftime("%Y-%m-%d")
               print(date)
               
               # find answer views                       
               answer_views= part_soup.find("span", {"class": "meta_num"})
               #print(answer_views.text)
               
               answer_views= convertnumber(answer_views.text)

               # find answers text     
               answer_text= part_soup.find("div", {"class": "ui_qtext_expanded"})
               answer_text= answer_text.text.replace('\n','').replace('\t','')                   
               
               #write answer elements to file
               s=  str(question_id) +  "\t"+ user_id + "\t"+ str(date) + "\t" +   str(answer_views) + "\t"+ str(answer_text) +'\t' +  str(questions_topics_text)+ "\n" 
               file_answers.write(s.encode('utf8'))
      
             
            except Exception as e1: # Mostly because user is anonymous ,  continue without saving anything 
               print('---------------There is an Exception-----------')
               print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e1).__name__, e1)
               print(str(e1))
        
        # change ip address after each 1000 request
        if (k % 1000==0):
           browser.quit()
           browser= connectchrome()
        print ("*************************************************************************")
        if k==74256 :
           loop= False
    print("--- %s seconds ---" % (time.time() - start_time))        
    browser.quit()  
 
def main():

    crawlQuestionData("/home/youcef/Documents/quora_top_urls.txt")
    return 0

if __name__ == "__main__": main()       
             
      
