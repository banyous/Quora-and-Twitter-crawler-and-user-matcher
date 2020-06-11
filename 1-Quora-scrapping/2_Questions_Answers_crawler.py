# -*- coding: utf-8 -*-
import sys
sys.path
DEBUG = 1
import os
import random
import time
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import dateparser
from connectChrome import connectchrome


##############################################################################################
# This script takes as input a list of Quora question URLs contained in the quora_urls.txt (URLs are line separated)
# Than collects  the answers to each question
# Each answer is saved in a separate line that contains the following informations:
#  Quest-ID | Date | Author(answerer)-ID | Quest-tags | Answer Text
# The answers are saved in the answers.txt file
##############################################################################################

def convertnumber(number):
    if 'k' in number:
        n=float(number.replace('k', '').replace(' ', ''))*1000
    elif 'm' in number:
        n=float(number.replace('m', '').replace(' ', ''))*1000000
    else:
        n=number
    return int(n)   

# method for loading all Quora answers ( a default Quora Question page shows only 7 Answers)
def scrolldown(self):
    last_height = self.page_source
    loop_scroll=True
    attempt = 0
    # we generate a random waiting time between 2 and 4
    waiting_scroll_time=round(random.uniform(2, 4),1)
    print('scrolling down...')
    while loop_scroll:
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        self.execute_script("window.scrollBy(0,-200)")
        time.sleep(1)
        self.execute_script("window.scrollBy(0,-200)")
        time.sleep(1)
        new_height=self.page_source
        if new_height == last_height:
            # in case of not change, we increase the waiting time
            waiting_scroll_time= round(random.uniform(5, 7),1)
            attempt += 1
            if attempt==3:# in the third attempt we end the scrolling
                loop_scroll=False
            #print('attempt',attempt)
        else:
            attempt=0
            waiting_scroll_time=round(random.uniform(2, 4),1)
        last_height=new_height
    posts = self.find_elements_by_css_selector("div.AnswerBase")
    print(" total answers found : ",len(posts))


# function that read Questions' URLs  from file and crawl the answers
def crawlQuestionData(file):
    start_time = time.time()
    # Open question url file
    file_question_urls = open(file, mode = 'r') # input file
    file_answers = open("answers.txt", mode='a') # output file containing all answers
    questions_urls = file_question_urls.readlines()
    browser= connectchrome()
    # starting line
    k = 0
    limit= len(questions_urls)
    while True:
        current_line= questions_urls[k]
        print('processing question number  : '+ str(k))
        k+=1
        if k == limit:
            break
        if '/unanswered/' in str(current_line):
            print('answer is unanswered')
            continue     
        print ("*************************************************************************")
        if (DEBUG): print(current_line)
        question_id = current_line
        # opening Question page
        try:
            browser.get(current_line)
        except Exception as OpenEx:
            print('cant open question link : ',current_line)
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(OpenEx).__name__, OpenEx)
            print(str(OpenEx))
            continue
        scrolldown(browser)
        continue_reading_buttons = browser.find_elements_by_xpath("//a[@role='button']")
        time.sleep(2)
        for button in continue_reading_buttons:
            try:
                ActionChains(browser).click(button).perform()
                time.sleep(1)
            except:
                continue
        time.sleep(2)
        html_source = browser.page_source
        soup = BeautifulSoup(html_source,"html.parser")
        with open('/home/youcef/Desktop/page.txt','w') as fff:
             fff.write(str(soup))
        question_id = current_line.rsplit('/', 1)[-1]
        question_id = question_id[:-1]
        # find title 
        title= current_line.replace("https://www.quora.com/","")
        # find question's topics
        questions_topics= soup.findAll("span", {"class": "TopicName"})
        questions_topics_text=[]
        for topic in questions_topics : questions_topics_text.append(topic.text)
        # number of answers
        # not all answers are saved!
        # answers that collapsed, and those written by annonymous users are not saved
        try:
            split_html = html_source.split('class="pagedlist_item"')
        except Exception as notexist :#mostly because question is deleted by quora
            print('question no long exists')
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(notexist).__name__, notexist)
            print(str(notexist))
            continue    
        # The underneath loop will generate len(split_html)/2 exceptions, cause answers in split_html
        # are eitheir in Odd or Pair positions, so ignore printed exceptions.
        for i in range(1, len(split_html)):
            try:
                part = split_html[i]
                part_soup = BeautifulSoup(part,"html.parser" )
                print('===============================================================')
                #find users names of answers authors
                authors=  part_soup.find("a", {"class": "u-flex-inline"}, href=True)
                user_id = authors['href'].rsplit('/', 1)[-1]
                print(user_id)
                # find answer dates
                answer_date= part_soup.find("a", {"class": "answer_permalink"})
                try:
                    date=answer_date.text
                    if ("Updated" in date):
                       date= date[8:]
                    else:
                       date= date[9:]
                    date=dateparser.parse(date).strftime("%Y-%m-%d")
                except: # when updated or answered in the same week (ex: Updated Sat)
                    date=dateparser.parse("7 days ago").strftime("%Y-%m-%d")
                print(date)
                # find answers text
                answer_text = part_soup.find("div", {"class": "ui_qtext_expanded"})
                # print(" answer_text", answer_text)
                answer_text = answer_text.text
                #write answer elements to file
                s=  str(question_id) +'\t' + str(date) + "\t"+ user_id + "\t"+ str(questions_topics_text) + "\t" +    str(answer_text)  + "\n"
                print("wrting down the answer...")
                file_answers.write(s)
            except Exception as e1: # Most times because user is anonymous ,  continue without saving anything
               print('---------------There is an Exception-----------')
               print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e1).__name__, e1)
               print(str(e1))
        print ("*************************************************************************")
        # we sleep every while in order to avoid IP ban
        if k%10==0:
            time.sleep(10)
    print("--- %s seconds ---" % (time.time() - start_time))        
    browser.quit()
 
def main():
    # We merged all Questions urls crawled by 1-Questions_URLs_crawler.py into one file (quora_urls.txt)
    crawlQuestionData((os.path.join(sys.path[0]+"/quora_urls.txt")))

if __name__ == "__main__": main()