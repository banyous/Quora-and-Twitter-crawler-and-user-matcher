# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from connectChrome import connectchrome
import time
import os
import sys
import requests
from requests.exceptions import ConnectionError
from string import digits    
import urllib
import glob   
from PIL import Image
import imagehash
from pprint import pprint
from shutil import copyfile
#from find_last_matching_account import find_last_matching
from termcolor import colored
import unidecode
import face_recognition
from collections import Counter, OrderedDict
import subprocess
DEBUG = 1

################################################################################################################
#This code matches Quora user accounts to their correspondant accounts in Twitter
# It takes a Quora user-IDs list from Qusers_ids.txt file
# Than look for correspending Twitter account for each Quora user-ID
# By first retrieving the same Quora-ID in Twitter (with some string modifications)
# and than matching the profile photos of the Quora and Twitter accounts (by face recongnition and image similarity)
# True matching accounts (QuoraID TwitterID) are then saved to true_matching.txt
################################################################################################################
# get line index of last found user matching
def find_last_matching():
    f_Health_users = open(os.path.join(sys.path[0],'Health-users.txt'), mode='r')
    file_all_accounts = f_Health_users.readlines()
    f_Health_users.close()
    f_dual_accounts = open(os.path.join(sys.path[0],'dual_accounts.txt'), mode='r')
    file_dual_accounts = f_dual_accounts.readlines()
    f_dual_accounts.close()
    index_last=0
    if len(file_dual_accounts)>0:
        #for user_id in file_dual_accounts:
            user_id=file_dual_accounts[-1]
            #print(user_id)
            user_id= user_id.split('\t')[0]
            matches = [line for line in file_all_accounts if user_id.strip('\n') in line]
            index = file_all_accounts.index(matches[0])
            if index>index_last:
                index_last=index
    return index_last

#check if twitter profile does exists     
def valid_twitter_url(browser):
        exists=False
        try:
            if not browser.page_source.__contains__("Something went wrong."):
                exists=True
        except Exception as e0:
            print('cant access twitter account')
            print(e0)
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e0).__name__, e0)
            pass
        return exists

def check_similarity(user_id,checking):  #return boolean
#when checking equal 'quora': check wether user_id quora profile photo is default 
#when checking is 'twitter': check wether user_id  twitter profile photo is default 
#when checking is else: check if  two photos of user_id and checking are similair or have same faces 

    path_photos_quora= os.path.join(sys.path[0]+'/quora-images/')
    path_photos_twitter=os.path.join(sys.path[0]+'/twitter-images/')
    os.makedirs(path_photos_quora, exist_ok=True)
    os.makedirs(path_photos_twitter, exist_ok=True)
    default_hash_quora=imagehash.average_hash(Image.open(os.path.join(sys.path[0]+'/default_quora_photo')))
    default_hash_quora2=imagehash.average_hash(Image.open(os.path.join(sys.path[0]+'/default_quora_photo_2')))
    default_hash_quora3=imagehash.average_hash(Image.open(os.path.join(sys.path[0]+'/default_quora_photo_3')))
    default_hash_quora4=imagehash.average_hash(Image.open(os.path.join(sys.path[0]+'/default_quora_photo_4')))
    default_hash_quora5=imagehash.average_hash(Image.open(os.path.join(sys.path[0]+'/default_quora_photo_5')))
    default_hash_twitter=imagehash.average_hash(Image.open(os.path.join(sys.path[0]+'/default_twitter_photo')))
    similarity=False
    
    if checking=='quora': # check if quora profile photo is default
        hash_quora = imagehash.average_hash(Image.open(path_photos_quora+user_id))
        if default_hash_quora -hash_quora <3  or default_hash_quora2 - hash_quora<3 or  default_hash_quora3 - hash_quora<3  or  default_hash_quora4 - hash_quora<3 or  default_hash_quora5 - hash_quora<3:
            similarity=True
    elif checking=='twitter': # check if twitter profile photo is default
        hash_twitter = imagehash.average_hash(Image.open(path_photos_twitter+user_id ))
        if hash_twitter - default_hash_twitter <3 :
           similarity=True
    else: # check if quora profile photo and twitter profile photo are similair or have same faces
        hash_quora = imagehash.average_hash(Image.open(path_photos_quora+user_id )) 
        hash_twitter = imagehash.average_hash(Image.open(path_photos_twitter+checking ))
        cutoff = 10                      
        if hash_quora - hash_twitter <cutoff: # the two photos are identical
            print (colored('images are identical', 'yellow'))
            similarity=True
        else:
            quora = face_recognition.load_image_file(path_photos_quora+user_id)
            twitter = face_recognition.load_image_file(path_photos_twitter+checking)   
            biden_encoding = face_recognition.face_encodings(quora)
            unknown_encoding = face_recognition.face_encodings(twitter)
            if len (biden_encoding)>0 and len(unknown_encoding)>0: 
                results = face_recognition.compare_faces([biden_encoding[0]],  unknown_encoding[0])
                print('faces detected')
                if results== [True]: # similair faces
                    similarity=True
                    print (colored('similarity is  True' , 'yellow'))
                else:
                    print('similarity is False')
            else:
                print('no face detected')    
    return similarity                                                    

def try_delete_file(file):
    try:
        os.remove(file)
    except OSError:
        pass    
def convertnumber(number):
    number=number.replace(',', '').replace(' ', '')
    if 'k' in number:
        n=float(number.replace('k', '').replace(' ', ''))*1000
    elif 'm' in number:
        n=float(number.replace('m', '').replace(' ', ''))*1000000
    elif 'K' in number:
        n=float(number.replace('K', '').replace(' ', ''))*1000
    elif 'M' in number:
        n=float(number.replace('M', '').replace(' ', ''))*1000000    
    else:
        n=number
    return int(n) 


#takes Quora user id file, check for each user if he has valid account url on twitter
# if yes check photo similarity of quora account and twitter account
# if photos similar or faces same then save user to list
def get_and_check_similarity_twitter_profile(fileu): 
    file_users= open(fileu,'r') # file containing quora users ids
    current_lines = file_users.readlines()
    print(len(current_lines))
    True_matching_accounts_file=open(os.path.join(sys.path[0] + '/true_matching.txt'), 'a')
    quora_images_directory = (os.path.join(sys.path[0]+'/quora-images/'))
    twitter_images_directory =(os.path.join(sys.path[0]+'/twitter-images/'))
    os.makedirs(quora_images_directory, exist_ok=True)
    os.makedirs(twitter_images_directory, exist_ok=True)
    lines= file_users.readlines()
    #start_line=find_last_matching() 
    start_line=0
    if start_line!=0:
        start_line+=1
    Nonstop=True
    browser = connectchrome()
    while Nonstop:
        line=current_lines[start_line]
        start_line+=1
        quora_user_id=line.strip()
        print('-------------------------')
        print ('processing user : ', quora_user_id,'    line : ', start_line-1)
        # i is number of User-id matching schemes between Qu and Tw
        i=0
        while i<2: # we will try 2 twitter ids: first replacing quora_id '-' with '' , second replacing '-' with '_'
            i+=1
            try: # check first if quora user profile url is still valid  
                url1= 'https://www.quora.com/profile/'+quora_user_id # quora profile url
                #r1 = requests.get(url1)
                browser.get(url1)
                time.sleep(2)
                soup1 = BeautifulSoup(browser.page_source,"html.parser")
                quora_photo=  soup1.find("img", {"class": "q-image qu-display--block"})['src'] #
                print('quora_photo   :',quora_photo)
                urllib.request.urlretrieve(quora_photo, quora_images_directory+quora_user_id)
                if not check_similarity(quora_user_id, 'quora') : # if quora user profile photo is not default
                    # check if twitter user profile exists
                    print('check if twitter user profile exists')
                    twitter_user_id= unidecode.unidecode(quora_user_id)
                    remove_digits = str.maketrans('', '', digits)
                    twitter_user_id = twitter_user_id.translate(remove_digits)    
                    if i==1: #first username matching scheme (ex : Albert-Enstein-195 ---> AlbertEnstein )
                        if len(twitter_user_id.split('-')) <3 and twitter_user_id.strip('\n')[-1]=='-' :
                        # if user is like 'kevin' or 'kevin-3' than try to find in twitter only one time
                             i=2 # go to next user
                        
                        twitter_user_id= twitter_user_id.replace('-','')  
                    else: #second username matching scheme (ex : Albert-Enstein-195 ---> Albert_Enstein
                        twitter_user_id=twitter_user_id.replace('-','_')
                        if twitter_user_id[-1:]=='_': twitter_user_id=twitter_user_id[:-1] 
                    print('looking  in twitter for  :', twitter_user_id)
                    url2=  "https://www.twitter.com/"+twitter_user_id+'/photo' #twitter profile url
                    #r2 = requests.get(url2)
                    print('twitter url : ',url2)
                    browser.get(url2)
                    time.sleep(2)
                    # if twitter page exists (is not private, nor suspended, nor deleted)
                    # then we will proceed further to check twitter photo similarity with quora photo
                    if valid_twitter_url(browser):
                        print('twitter account exists')
                        soup2=BeautifulSoup(browser.page_source,"lxml")
                        print('valid twitter account')
                        twitter_photo=  soup2.find("img")['src']
                        urllib.request.urlretrieve(twitter_photo, twitter_images_directory+ twitter_user_id)
                        if not check_similarity(twitter_user_id, 'twitter') : # if twitter profile photo is not default
                            if check_similarity(quora_user_id,twitter_user_id): # if profile photos are identical or have similair faces
                                ### use function to collect quora profile from soup1
                                ### use function to collect twitter profile from soup2
                                True_matching_accounts_file.write(quora_user_id + '\t' + twitter_user_id + '\n') # save username
                                i=2   # go to next matching scheme
                            else:
                                try_delete_file(quora_images_directory+quora_user_id)
                                try_delete_file(twitter_images_directory+twitter_user_id)

                        else:
                            try_delete_file(quora_images_directory+quora_user_id)
                            try_delete_file(twitter_images_directory+twitter_user_id)
                            print('twitter user profile photo is default...')
                    else:
                        try_delete_file(quora_images_directory+quora_user_id)
                        try_delete_file(twitter_images_directory+twitter_user_id)               
                else:
                    try_delete_file(quora_images_directory+quora_user_id)
                    print('quora user profile photo is default...')
                    i=2  # go to next user
            except requests.exceptions.ConnectionError: # if quora server refuses connection , we're sending too many requests, we will sleep for 100 seconds
                start_line-=1
                print("exception Connection refused ... Program will sleep for 100 seconds...")
                time.sleep(100)
                i=0
            except Exception as Exphoto: 
                print('exception : user no long exists in quora or in twitter')#most common reason for exception
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(Exphoto).__name__, Exphoto)
                i=2  # go to next user     
        if start_line==30000:
            Nonstop=False
    True_matching_accounts_file.close()
    file_users.close()

                   
def main():
    start_time = time.time()
    # Qusers_ids.txt is the output of the 1-Quora-scrapping module
    # we need to select the user_id  form the answers text file (second tab separated column)
    # and put it in a file named /Qusers_ids.txt
    get_and_check_similarity_twitter_profile(os.path.join(sys.path[0]+'/Qusers_ids.txt'))
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__": main()
