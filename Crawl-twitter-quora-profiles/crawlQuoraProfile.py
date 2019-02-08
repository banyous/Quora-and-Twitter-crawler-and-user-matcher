# -*- coding: utf-8 -*-
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os
import subprocess
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from connectChrome1 import connectchrome
#from crawlQuestionData import convertnumber
import time
DEBUG = 1
# from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import dateparser
import json
import sys 

def convertnumber(number):
    if 'k' in number:
        n=float(number.replace('k', '').replace(' ', ''))*1000
    elif 'm' in number:
        n=float(number.replace('m', '').replace(' ', ''))*1000000
    else:
        n=number
    return int(n)   

def scrolldown(browser, repeat):        
    print('scrolling down ...')
    src_updated = browser.page_source
    src = ""
    loopscroll=True
    limit=0
    sleep=2
    scrollcount=0
    while  loopscroll:
        scrollcount+=1
        if scrollcount>30: # we will scroll down max 30 times, in order to get only top 300 answers 
            loopscroll=False
            break
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep)
        src = src_updated
        src_updated = browser.page_source 
        if src == src_updated:
            if repeat==True:
                limit+=1
                if limit==1:
                    sleep=5
                else:
                    loopscroll=False   
            else:
                loopscroll=False
           
        else:
            limit=0
            sleep=5
                
# Gather user data and save into csv file
def crawlUser():
    start_time = time.time()
    
    if (DEBUG): print("In crawlUser...")
    file_users = open("/home/youcef/Desktop/0quorausers.txt", mode='r') #
    
    current_lines = file_users.readlines()
    browser= connectchrome()
    
    loop=0
    wait = WebDriverWait(browser, 10)
    k=27
    #27
    loop=True
    while(loop):
        
        # a dict to contain information about profile 
        quora_profile_information=dict()
        
        current_line= current_lines[k].replace(' ','')
        current_line=current_line.replace('http', 'https')
        if current_line =='':
            print('empty line')
            continue
        
        #print('processing user :', current_line)
        loop+=1
        # Open browser to current_question_url
        user_id0=current_line.strip('\n').strip()
        user_id1=re.findall('[A-Z][a-z]*',user_id0)
        user_id='-'.join(user_id1)
        print('user id is: ', user_id)
        url= "https://www.quora.com/profile/"+user_id
        file_user_profile = open("/home/youcef/Desktop/0usersq/"+user_id+'.json', "w", encoding="utf8")
        quora_profile_information['user_id']=user_id
        print('######################################')
        print(url)
        print('user number  :',k)
        browser.get(url)        
        time.sleep(2)           
        k+=1
          
            
        # get profile description
        try: 
            description= browser.find_element_by_class_name('IdentityCredential')
            description= description.text.replace('\n', ' ')
            print(description)
            
        except:
            description=''
            print('no description')
        quora_profile_information['description']=description 
        
        # get profile bio        
        try:
           more_button = browser.find_elements_by_link_text('(more)')
           ActionChains(browser).move_to_element(more_button[0]).click(more_button[0]).perform()
           time.sleep(0.5)
           profile_bio = browser.find_element_by_class_name('ProfileDescriptionPreviewSection')
           profile_bio_text=profile_bio.text.replace('\n', ' ')
           print(profile_bio_text)
        except Exception as e:
           print('no profile bio')
           print(e)
           profile_bio_text=''
        
        quora_profile_information['profile_bio']=profile_bio_text
        
        html_source = browser.page_source
        source_soup = BeautifulSoup(html_source,"html.parser")
        
        #get location 
        print('trying to get location')
        location='None'
        try:
            location1= (source_soup.find(attrs={"class":"LocationCredentialListItem"}))
            location2= (location1.find(attrs={"class":"main_text"})).text
            location= location2.replace('Lives in ','')
        except Exception as e3:
            print('exception regarding finding location')
            print(e3)
            pass
        
        quora_profile_information['location']=location
        #get total number of views
        total_views='0'
        try:
            #views=wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "AnswerViewsAboutListItem.AboutListItem")))
            views= (source_soup.find(attrs={"class":"AnswerViewsAboutListItem"}))            
            total_views=views.text.split("answer")[0]
        except Exception as e4:
            print('exception regarding finding number of views')
            print(e4)
            pass
        total_views=convertnumber(total_views)    
        print(location)        
        print("total_views")
        print(total_views)
        quora_profile_information['total_views']=total_views
        
        answers='0'
        questions='0'
        followers='0'
        following='0'
        print('trying to get answers stats')
        try:
            
            html_source = browser.page_source
            source_soup = BeautifulSoup(html_source,"html.parser")
            # Find user social attributes : #answers, #questions, #shares, #posts, #blogs, #followers, #following, #topics, #edits
            part = source_soup.find_all(attrs={"class":"layout_3col_left"})
            part_soup = BeautifulSoup(str(part),"html.parser" )
            profile_info= part_soup.find_all(attrs={"class":"list_count"})
            answers= profile_info[0].text.replace(',','')
            #print(answers)
            questions= profile_info[1].text.replace(',','')
            #print(questions)
            followers= profile_info[4].text.replace(',','')
            #print(followers)
            following= profile_info[5].text.replace(',','')
            #print(following)
             
        except Exception as ea:
            print('cant get profile attributes answers quesitons followers following')
            print (ea)
            time.sleep(1)
        
        quora_profile_information['nb_answers']=answers
        quora_profile_information['nb_questions']=questions
        quora_profile_information['nb_followers']=followers
        quora_profile_information['nb_following']=following
        json.dump(quora_profile_information,file_user_profile)
        file_user_profile.write('\n')
        #file_user_profile.write((s + '\n').encode('utf8'))
       
        # scroll down profile
        repeat=False
        if int(answers)>30:
            repeat=True
        if int(answers)>14:
            scrolldown(browser,repeat)       
       
        # get answers text       
        if int(answers)>0:
            print('scrolling down for answers collect')
            i=0
            more_button = browser.find_elements_by_link_text('(more)')
            
            for jk in range(0,len(more_button)):    
                
                ActionChains(browser).move_to_element(more_button[jk]).click(more_button[jk]).perform()
                time.sleep(1)
            
            html_source = browser.page_source
            source_soup = BeautifulSoup(html_source,"html.parser")
            split_html = html_source.split('feed_item inline_expand_item') 
            ans=1
            answers_list=[]
            print('len split html :', len(split_html))
            ansloop=True
            #for ans in range(0, len(split_html)-1):
            while ansloop:        
                try:  
                    
                    # a dict to contain information about each answer 
                    quora_answer_information=dict()              
                    part = split_html[ans]
                    part_soup = BeautifulSoup(part,"html.parser" )
                    ans+=1
                    if ans == len(split_html):
                        ansloop=False
                    #print('=====================')               
                    
                    #find answer text
                    answerText=  part_soup.find("div", {"class": "ui_qtext_expanded"})
                    #print(answerText.text)
                    answerLength= len(answerText.text)
                    '''answerText= answerText.text[:-7] # last 7 characters of answer are 'nb views 
                    if '...(more)Loading…' in answerText:
                        answerText= ' '.join(answerText.split('...(more)Loading…')[1:]) # delete first preview of answer, keep only extended answer'''
                    #print('length of answer ', len(answerText))   
                    #print(answerText)    
                    
                    #find answer's question url
                    answerQuestionUrl=  part_soup.find("a", {"class": "question_link"}, href=True)
                    answerQuestionUrl= answerQuestionUrl['href'][1:]
                    print(answerQuestionUrl)
                    #print (answerQuestionUrl)  
                    
                    #find answer data
                    date=part_soup.find("a", {"class": "answer_permalink"}) 
                    date=date.text
                    if ("Updated" in date):
                           date= date[8:]
                    else:
                           date= date[9:]
                    date= dateparser.parse(date).strftime("%Y-%m-%d")
                    #print(date)              
                    
                    quora_answer_information['answerQuestionUrl']= answerQuestionUrl
                    quora_answer_information['answerDate']= date
                    quora_answer_information['answerLength']= answerLength
                    quora_answer_information['answerText']= str(answerText)
                    answers_list.append(quora_answer_information)
                except Exception as eans: 
                    print('cant get answer info')
                    print (eans)
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(eans).__name__, eans)
                     
            for answer in answers_list:
                json.dump(answer,file_user_profile)
                file_user_profile.write('\n')
        file_user_profile.close()
        if (k % 100==0):
           browser.quit()
           time.sleep(5)
           browser= connectchrome()
        if k==28:
            loop= False
    browser.quit()    
    file_users.close()
    
    print(("Total users:{0}".format(str(loop))))
    print("--- %s seconds ---" % (time.time() - start_time))
    return 0
    
def main():

    crawlUser()

if __name__ == "__main__": main()
