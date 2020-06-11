from connectChrome import connectchrome
from bs4 import BeautifulSoup
import os
import datetime
import time
import csv
import sys

##############################################################################################
# This script takes as input a list of topics contained in the topics_file.txt (topics are line separated)
# Than checks if each topic exists in Quora website
# If yes, it will collect all questions urls and put them in topic_name.txt file in the /topics directory
##############################################################################################
# start time
start_time = datetime.datetime.now()
# read topics
topics_file = open((os.path.join(sys.path[0] + '/topics_file.txt')), mode='r', encoding='utf-8')
# the topic parsing index  ,
# If program stops for any reason After running
# you can manually change the topic_index to last parsed topic's index
topic_index=0
#connecting to chrome ..
driver=connectchrome()
topics_list=topics_file.readlines()
loop_limit=20#len(topics_list)
while True:
    topic_term=topics_list[topic_index].strip()
    topic_index += 1
    if topic_index==loop_limit:
        break
    # we ignore hashtags (optional)
    if (topic_term.startswith("#")):
        continue
    # Looking if the topic has an existing Quora url
    print('#########################################################')
    print('Looking for topic : ', topic_term)
    try:
        url = "https://www.quora.com/topic/" + topic_term.strip() + "/all_questions"
        print('starting new topic: ' + str(topic_term))
        print(str(url))
        driver.get(url)
    except Exception as e0:
        print('topic does not exist in Quora')
        print('exception e0')
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e0).__name__, e0)
        continue
    # get browser source
    html_source = driver.page_source
    question_count_soup = BeautifulSoup(html_source, 'html.parser')
    #  get total number of questions
    question_count_str = question_count_soup.find('a', attrs={'class': 'TopicQuestionsStatsRow'})
    if str(question_count_str)=='None':
        print('topic does not have questions...')
        continue
    question_count = question_count_str.contents[0].text
    # converting Kilo to digitis
    if 'k' in str(question_count):
        question_count = str(question_count).replace('k','')
        question_count = int(float(question_count)*1000)
        #print(type(question_count))
    print('number of questions for this topic : '+ str(question_count))
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    # infinite while loop, break it when you reach the end of the page or not able to scroll further.
    # Note that Quora
    if int(question_count)>10: # if there is more than 10 questions, we need to scroll down the profile to load remaining questions
        start_time_sd = time.time()
        max_time=  int(question_count)*0.25
        if int(question_count)> 8000:
            max_time=1800
        while True:
            scrolling_attempt = 0
            scroll_waiting_time = 2
            # try to scroll 3 times in case of slow connection
            while True:
                print('@@@@@@@@@@@@@@@@@@@@!trying for time number ',scrolling_attempt)
                # Scroll down to one page length
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait to load page
                time.sleep(scroll_waiting_time)
                # get page height in pixels
                new_height = driver.execute_script("return document.body.scrollHeight")
                # break this loop when you are able to scroll further
                if new_height != last_height:
                   break
                # else  we do 3 attempts of scrolling down with different pause_time in each attempt
                scrolling_attempt+=1
                if scrolling_attempt==1:
                    scroll_waiting_time = 4
                elif scrolling_attempt==2:
                    if int(question_count)>2000:
                        scroll_waiting_time = 15
                    elif int(question_count)>500:
                        scroll_waiting_time = 7
                    else : # if number of questions is small(<500) than quit
                        break
                else : # after the third attempt we quit
                    break
            if new_height == last_height:  # not able to scroll further, break the loop
                break
            last_height = new_height
            # check if the  total time exceeds the limit
            total_time=time.time() - start_time_sd
            if total_time> max_time:
                print('max time exceeded')
                break
    # next we harvest all questions URLs that exists in the Quora topic's page
    print('getting ressources ...')
    # get html page source
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    # question_link is the class for questions
    question_link = soup.find_all('a', attrs={'class': 'question_link'}, href=True)
    # add questions to a set for uniqueness
    question_set = set()
    for ques in question_link:
        question_set.add(ques)
    # write content of set to a file called question_urls.txt
    questions_directory = 'topics/'
    os.makedirs('topics/', exist_ok=True)
    file_name = questions_directory + '/' + topic_term.strip('\n') + '_question_urls.txt'
    file_question_urls = open(file_name, mode='w', encoding='utf-8')
    writer = csv.writer(file_question_urls)
    for ques in question_set:
        link_url = "http://www.quora.com" + ques.attrs['href']
        #print(link_url)
        writer.writerows([[link_url]])
    #sleeping each 20 requests (can be changed)
    sleep_time=5
    if topic_index % 20== 0:
       print('quitting chrome')
       driver.quit()
       time.sleep(sleep_time)
       driver=connectchrome()

# finish time
end_time = datetime.datetime.now()
print(' Crawling Quora topics is finished, it tooks a time of  : ',end_time-start_time)
