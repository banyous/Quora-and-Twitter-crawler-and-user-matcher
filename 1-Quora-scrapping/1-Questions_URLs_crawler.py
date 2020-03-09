from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import datetime
import time
import csv
import sys


# this code takes as input a file containing topics keywords file : terms_file.txt
# and gives as output for each keyword topic a file containing quora questions urls related to the topic 

def connectchrome():

    # instantiate a chrome options object so you can set the size and headless preference
    options = Options()
    options.add_argument('--headless')
    options.add_argument('log-level=3')
    options.add_argument("--incognito")
    driver = webdriver.Chrome(chrome_options=options)
    driver.execute_script('window.scrollTo(0, 0);')
    # download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads
    # and put it in the current directory
    chromedriver = "/home/youcef/Documents/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver     
    browser = webdriver.Chrome(chrome_options=options) 
    browser.get('https://www.quora.com/')
    time.sleep(2)
    return browser
# start time
start_time = datetime.datetime.now()

# read topics form a file
file_question_topics = open("terms_file.txt", mode='r', encoding='utf-8')
cc=1708
driver=connectchrome()
lines=file_question_topics.readlines()
parsing_loop=True
print(len(lines))
while parsing_loop:
           line=lines[cc]
           cc+=1
           topic=line.strip()
           if (topic.startswith("#")):
                    continue
           
           
           # give the url to scrape
          
           try:
                print('###################')
                print('starting new topic: ' + str(topic))
                url = "https://www.quora.com/topic/" + topic.strip('\n') + "/all_questions"
                print(str(url))
                driver.get(url)
           except Exception as e0:
                print('exception e0')
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e0).__name__, e0)
                continue     

                     
           # define pause time for browser
           SCROLL_PAUSE_TIME = 2

           # get browser source
           html_source = driver.page_source
           question_count_soup = BeautifulSoup(html_source, 'html.parser')

           #  get total number of questions
           question_count_str = question_count_soup.find('a', attrs={'class': 'TopicQuestionsStatsRow'})
           
           if str(question_count_str)=='None':
               print('topic does not exist in Quora')
               continue
           
           question_count = question_count_str.contents[0].text 
           if 'k' in str(question_count):
                      question_count = str(question_count).replace('k','')
                      question_count = int(float(question_count)*1000)
                      #print(type(question_count))
           print('number of questions for this topic : '+ str(question_count))

           # Get scroll height
           last_height = driver.execute_script("return document.body.scrollHeight")
           question_set = set()
           # infinite while loop, break it when you reach the end of the page or not able to scroll further.
           if int(question_count)>10:
               start_time_sd = time.time()
               max_time=  int(question_count)*0.25
               if int(question_count)> 8000:
                    max_time=1800
               while True:
                          
                          i = 0
                          # try to scroll 5 times in case of slow connection
                          while True:
                                     # Scroll down to one page length
                                     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                                     # Wait to load page
                                     time.sleep(SCROLL_PAUSE_TIME)

                                     # get page height in pixels
                                     new_height = driver.execute_script("return document.body.scrollHeight")
              
                                     # break this loop when you are able to scroll futher
                                     if new_height != last_height:
                                           break
                                     if i==1:
                                        SCROLL_PAUSE_TIME = 4   
                                     if i==2:
                                        if int(question_count)>500 and int(question_count)<2000:
                                            SCROLL_PAUSE_TIME = 7
                                        elif int(question_count)>2000:
                                            SCROLL_PAUSE_TIME = 15    
                                        elif int(question_count)<500:
                                            break
                                     if i==3:
                                        break
                                     i += 1
                          SCROLL_PAUSE_TIME = 2    
                          # not able to scroll further, break the infinite loop
                          new_height = driver.execute_script("return document.body.scrollHeight")
                          if new_height == last_height:
                                     break
                          last_height = new_height
                          total_time=time.time() - start_time_sd
                          if total_time>max_time:
                            print('max time exceeded')
                            break
                      
                 
                      
           print('getting ressources ...')
           # get html page source
           html_source = driver.page_source
           soup = BeautifulSoup(html_source, 'html.parser')
           # question_link is the class for questions
           question_link = soup.find_all('a', attrs={'class': 'question_link'}, href=True)

           # add questions to a set for uniqueness
           for ques in question_link:
                  question_set.add(ques)
                
           
           # write content of set to a file called question_urls.txt
           questions_directory = 'topics/'
           os.makedirs('topics/', exist_ok=True)
           file_name = questions_directory + '/' + topic.strip('\n') + '_question_urls.txt'
           file_question_urls = open(file_name, mode='w', encoding='utf-8')
           writer = csv.writer(file_question_urls)
           for ques in question_set:
                      link_url = "http://www.quora.com" + ques.attrs['href']
                      #print(link_url)
                      writer.writerows([[link_url]])
           
           #sleeping each 300 requests
           if cc % 300== 0:
               print('quitting chrome')
               driver.quit()
               time.sleep(6)
               driver=connectchrome()
           #loop_limit can be adjusted based on the number of requests we want to send 
           loop_limit=3000
           if cc==loop_limit:
            parsing_loop=False
           
# finish time
end_time = datetime.datetime.now()
print(end_time-start_time)
