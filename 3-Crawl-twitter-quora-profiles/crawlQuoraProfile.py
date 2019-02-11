# -*- coding: utf-8 -*-
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
from connectChrome import connectchrome
from crawlQuestionData import convertnumber
import time
DEBUG = 1
# from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


# Gather user data and save into csv file
def crawlUser():
    start_time = time.time()
    if (DEBUG): print("In crawlUser...")
    file_users = open("users0.txt", mode='r') #
    file_users_profiles = open("users-profiles.txt", mode='ab')
    current_lines = file_users.readlines()
    browser= connectchrome()
    loop=0
    wait = WebDriverWait(browser, 10)
    k=6615
    loop=True
    while(True):
        current_line= current_lines[k].replace(' ','')
        current_line=current_line.replace('http', 'https')
        if current_line =='':
            print('empty line')
            continue
        k+=1
        print('processing user :', current_line)
        loop+=1
        # Open browser to current_question_url
        user_id=current_line.strip('\n')
        url= "https://www.quora.com/profile/"+current_line
        print(url)
        browser.get(url)
        time.sleep(2)
        try: 
            description= browser.find_element_by_class_name('IdentityCredential')
            description= '{'+description.text.replace('\n', ' ')+'}'
            print(description)
        except:
            description='{}'
            print('no description')
        # get profile bio
        
        try:
           more_button = browser.find_elements_by_link_text('(more)')
           ActionChains(browser).move_to_element(more_button[0]).click(more_button[0]).perform()
           time.sleep(0.5)
           profile_bio = browser.find_element_by_class_name('ProfileDescriptionPreviewSection')
           
           #profile_bio = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "AboutSection")))
           profile_bio_text='{'+profile_bio.text.replace('\n', ' ')+'}'
           print(profile_bio_text)
        except Exception as e:
           print('no profile bio')
           print(e)
           profile_bio_text='{}'
         
        #views_check= wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "AboutListItem AnswerViewsAboutListItem")))
        html_source = browser.page_source
        source_soup = BeautifulSoup(html_source,"html.parser")
        
        #get location 
        location='None'
        try:
            location1= (source_soup.find(attrs={"class":"LocationCredentialListItem"}))
            location2= (location1.find(attrs={"class":"main_text"})).text
            location= location2.replace('Lives in ','')
        except Exception as e3:
            print('e3')
            print(e3)
            pass
            
        #get total number of views
        total_views='0'
  
        try:
            views=wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "AnswerViewsAboutListItem")))
            views= views.text.split('\n')   
            total_views= views[0].replace('answer views','')
        except Exception as e4:
            print('e4')
            print(e4)
            pass
        total_views=convertnumber(total_views)    
        print(location)        
        print("total_views")
        print(total_views)
        gogo=0
        go=True
        answers='-1'
        questions='-1'
        followers='-1'
        following='-1'
        while go:
            try:
                if gogo>1:
                    browser.get(url)
                    time.sleep(4)
                    html_source = browser.page_source
                    source_soup = BeautifulSoup(html_source,"html.parser")
                # Find user social attributes : #answers, #questions, #shares, #posts, #blogs, #followers, #following, #topics, #edits
                part = source_soup.find_all(attrs={"class":"layout_3col_left"})
                part_soup = BeautifulSoup(str(part),"html.parser" )
                profile_info= part_soup.find_all(attrs={"class":"list_count"})
                answers= profile_info[0].text
                #print(answers)
                questions= profile_info[1].text
                #print(questions)
                followers= profile_info[4].text
                #print(followers)
                following= profile_info[5].text
                #print(following)
         
                
                
                #printing retrived profile attributes to file 
 
                go=False  
            except Exception as ea:
                print('cant get profile attributes answers quesitons followers following')
                print (ea)
                time.sleep(1)
                gogo+=1
                if gogo==3: 
                    go=False
                    
            
        #if (loop % 100==0):
           #browser.quit()
           #time.sleep(5)
           #browser= connectchrome()
        if k==22404:
            loop= False
        print('##################')
               
        s = str(user_id) + "\t" + str(total_views)+ '\t'+ str(location)+ '\t'+ str(description)+'\t'+ str(profile_bio_text) + "\t" + str(answers) + "\t" + str(questions) +"\t" + followers + "\t" + following 
        #if (DEBUG): print(s)
        file_users_profiles.write((s + '\n').encode('utf8'))
        current_line = file_users.readline()
    browser.quit()    
    file_users.close()
    file_users_profiles.close()
    print(("Total users:{0}".format(str(loop))))
    print("--- %s seconds ---" % (time.time() - start_time))
    return 0
