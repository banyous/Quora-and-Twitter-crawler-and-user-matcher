# -*- coding: utf-8 -*-
DEBUG = 1
import os
import time
import subprocess
import json
import sys
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from connectChrome import connectchrome
from datetime import datetime, timedelta
import dateparser

################################################################################
#This code takes a list of Quora Users IDs (from /True_matching.txt (first column))
#For each UserID it will scrap the profile informations(Stats and Answers text)
#The profile data is saved in the /Qusers folder under UserID.txt filename
################################################################################
# remove 'k'(kilo) and 'm'(million) from Quora numbers
def convertnumber(number):
    if 'k' in number:
        n=float(number.replace('k', '').replace(' ', ''))*1000
    elif 'm' in number:
        n=float(number.replace('m', '').replace(' ', ''))*1000000
    else:
        n=number
    return int(n)

# convert Quora dates (such as 2 months ago) to DD-MM-YYYY format
def convertDateFormat(dateText):
    try:
        if ("Updated" in dateText):
            date = dateText[8:]
        else:
            date = dateText[9:]
        date = dateparser.parse(dateText).strftime("%Y-%m-%d")
    except:  # when updated or answered in the same week (ex: Updated Sat)
        date = dateparser.parse("7 days ago").strftime("%Y-%m-%d")
    return date

# for loading all profile content
def scrolldown(browser, repeat):
    print('scrolling down ...')
    src_updated = browser.page_source
    src = ""
    scroll_attempt=0
    sleep=2
    scrollcount=0
    while  True:
        scrollcount+=1
        if scrollcount>30: # we will scroll down max 30 times, in order to get only last 300 answers
            break
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep)
        src = src_updated
        src_updated = browser.page_source
        if src == src_updated:
            if repeat==True:
                scroll_attempt+=1
                if scroll_attempt==1:
                    sleep=10
                else:
                    break
            else:
                break

        else:
            scroll_attempt=0
            sleep=2

# Main crawling function
# Gather user data and save into txt tab separated file
# (If you have proxies, you can add the two arguments : proxies and proxy_index
# and uncomment all proxy lines in crawlUser() and Main())

def crawlUser(QT_IDs_file):#,proxies,proxy_index):
    ##### two lines below are proxy parameters (use them if you have many proxies)
    # os.environ['http_proxy']=proxies[proxy_index]
    # current_proxy_index=proxy_index
    print('_______________________________________________________________')
    QT_IDs = open(sys.path[0] + QT_IDs_file, mode='r') #
    QIDs = [line.strip().split('\t')[0] for line in QT_IDs.readlines()]
    browser= connectchrome()
    wait = WebDriverWait(browser, 10)
    dir_path = os.path.join(sys.path[0] + "/Qusers/")
    # find starting line : current line, which starts from the index of last crawled user
    current_index = -1
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        try:
            current_index= len([name for name in os.listdir(dir_path) if os.path.isfile(dir_path+name)])-2
        except:
            pass
    # Loop over the QuoraIDs to scrap their profile content
    while True:
        current_index+=1
        if current_index >=len(QIDs):
            print('Crawling finished...All users parsed from file...Please bring new Users IDs...:)')
            break
        # a dict to contain information about profile 
        quora_profile_information=dict()
        current_line= QIDs[current_index].strip()
        current_line=current_line.replace('http', 'https')
        if current_line =='':
            print('empty line')
            continue
        # we change proxy and sleep every 200 request (number can be changed)
        if (current_index % 200==199):
            # current_proxy_index=current_proxy_index + 13
            # if current_proxy_index>81:
            #     current_proxy_index=proxy_index
            # os.environ['http_proxy']=proxies[current_proxy_index]
            # print ('changed proxy to :', current_proxy_index)
            time.sleep(10)
        user_id=current_line.split('\t')[0]
        url= "https://www.quora.com/profile/"+user_id
        print(dir_path+user_id+'.json')
        file_user_profile = open(dir_path+user_id+'.json', "w", encoding="utf8")
        quora_profile_information['user_id']=user_id
        print('#########################################')        
        print('processing quora user number : ', current_index, '    ', url)
        browser.get(url)        
        time.sleep(2) 
        # get profile description
        try: 
            description= browser.find_element_by_class_name('IdentityCredential')
            description= description.text.replace('\n', ' ')
            #print(description)
        except:
            description=''
            #print('no description')
        quora_profile_information['description']=description
        # get profile bio        
        try:
           more_button = browser.find_elements_by_link_text('(more)')
           ActionChains(browser).move_to_element(more_button[0]).click(more_button[0]).perform()
           time.sleep(0.5)
           profile_bio = browser.find_element_by_class_name('ProfileDescriptionPreviewSection')
           profile_bio_text=profile_bio.text.replace('\n', ' ')
           #print(profile_bio_text)
        except Exception as e:
           #print('no profile bio')
           #print(e)
           profile_bio_text=''
        quora_profile_information['profile_bio']=profile_bio_text
        html_source = browser.page_source
        source_soup = BeautifulSoup(html_source,"html.parser")
        #get location 
        #print('trying to get location')
        location='None'
        try:
            location1= (source_soup.find(attrs={"class":"LocationCredentialListItem"}))
            location2= (location1.find(attrs={"class":"main_text"})).text
            location= location2.replace('Lives in ','')
        except Exception as e3:
            #print('exception regarding finding location')
            #print(e3)
            pass
        quora_profile_information['location']=location
        #get total number of views
        total_views='0'
        try:
            #views=wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "AnswerViewsAboutListItem.AboutListItem")))
            views= (source_soup.find(attrs={"class":"ContentViewsAboutListItem"}))            
            total_views=views.text.split("content")[0]
        except Exception as e4:
            ###print('exception regarding finding number of views')
            ###print(e4)
            pass
        #print(total_views)
        #print('@@@@@@@@@')
        total_views=convertnumber(total_views)    
        print(' location : ',location)        
        print("total_views",total_views)
        #print(total_views)
        quora_profile_information['total_views']=total_views
        nbanswers='0'
        nbquestions='0'
        nbfollowers='0'
        nbfollowing='0'
        #print('trying to get answers stats')
        try:
            html_source = browser.page_source
            source_soup = BeautifulSoup(html_source,"html.parser")
            # Find user social attributes : #answers, #questions, #shares, #posts, #blogs, #followers, #following, #topics, #edits
            part = source_soup.find_all(attrs={"class":"layout_3col_left"})
            part_soup = BeautifulSoup(str(part),"html.parser" )
            profile_info= part_soup.find_all(attrs={"class":"list_count"})
            nbanswers=browser.find_element_by_xpath("//div[@class='q-text qu-medium qu-fontSize--small qu-color--red' and text()[contains(.,'Answer')]]")
            nbanswers=nbanswers.text.strip('Answers').strip()
            print('answers',nbanswers)
            nbquestions =browser.find_element_by_xpath("//div[@class='q-text qu-medium qu-fontSize--small qu-color--gray_light' and text()[contains(.,'Question')]]")
            nbquestions=nbquestions.text.strip('Questions').strip()
            print("questions ",nbquestions)
            nbfollowers= browser.find_element_by_xpath("//div[@class='q-text qu-medium qu-fontSize--small qu-color--gray_light' and text()[contains(.,'Follower')]]")
            nbfollowers=nbfollowers.text.strip('Followers').strip()
            print("followers ",nbfollowers)
            nbfollowing= browser.find_element_by_xpath("//div[@class='q-text qu-medium qu-fontSize--small qu-color--gray_light' and text()[contains(.,'Following')]]")
            nbfollowing = nbfollowing.text.strip('Following').strip()
            print("following ",nbfollowing)
             
        except Exception as ea:
            print('cant get profile attributes answers quesitons followers following')
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(ea).__name__, ea)
            time.sleep(1)
        # writing answers stats to file
        quora_profile_information['nb_answers']=nbanswers
        quora_profile_information['nb_questions']=nbquestions
        quora_profile_information['nb_followers']=nbfollowers
        quora_profile_information['nb_following']=nbfollowing
        json.dump(quora_profile_information,file_user_profile)
        file_user_profile.write('\n')

        # scroll down profile for loading all answers
        repeat=False
        if int(nbanswers)>30:
            repeat=True
        if int(nbanswers)>9:
            scrolldown(browser,repeat)
        # get answers text (we click on (more) button of each answer)
        if int(nbanswers)>0:
            #print('scrolling down for answers collect')
            i=0
            # Find and click on all (more)  to load full text of answers
            more_button = browser.find_elements_by_xpath("//div[contains(text(), '(more)')]")
            print('nb more buttons',len(more_button))
            for jk in range(0,len(more_button)):
                ActionChains(browser).move_to_element(more_button[jk]).click(more_button[jk]).perform()
                time.sleep(1)
            try:
                questions_and_dates_tags= browser.find_elements_by_xpath("//a[@class='q-box qu-cursor--pointer qu-hover--textDecoration--underline' and contains(@href,'/answer/') and not(contains(@href,'/comment/')) and not(contains(@style,'font-style: normal')) ]")
                questions_link=[]
                questions_date=[]
                #filtering only unique questions and dates
                for QD in questions_and_dates_tags:
                    Qlink= QD.get_attribute("href").split('/')[3]
                    if Qlink not in questions_link:
                        questions_link.append(Qlink)
                        questions_date.append(QD.get_attribute("text"))

                questions_date=[convertDateFormat(d) for d in questions_date]
                answersText = browser.find_elements_by_xpath("//div[@class='q-relative spacing_log_answer_content']")
                answersText=[' '.join(answer.text.split('\n')[:]).replace('\r', '').replace('\t', '').strip() for answer in answersText]
            except Exception as eans:
                print('cant get answers')
                print (eans)
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(eans).__name__, eans)
                continue
            # writing down answers ( date+ Question-ID + Answer text)
            for ind in range(0,int(nbanswers)):
                file_user_profile.write(questions_date[ind] +'\t' + questions_link[ind] + '\t' + answersText[ind] + '\n')
        file_user_profile.close()
    browser.quit()    
    QT_IDs.close()



def main():
    start_time = time.time()
    # commented lines below are for proxies settings
    # proxy_index=int(sys.argv[1])
    # input_file=sys.argv[2]
    # proxies=[]
    # with open ('proxies.txt','r') as f:
    #     for line in f:
    #         proxies.append(line.strip())
    # proxy_index=int(sys.argv[1])
    # print('Proxy :', proxy_index)
    input_file='/true_matching.txt'
    crawlUser(input_file)#,proxies,proxy_index)
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__": main()
