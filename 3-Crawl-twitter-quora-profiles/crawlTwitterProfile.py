import tweepy #https://github.com/tweepy/tweepy
import json
import sys
import os
import time

 
 
 
#collect twitter user profile (tweets) and store them into json file
 
consumer_key = 'nt6NDq44qL2BFSeq8iajMHA6r'
consumer_secret = 'XpwIx4AnhgOWVIYsHPlXZNPHmXr7zSGPGXMyVqyEdMzNLMUqWw'
access_key = '302685662-PMYXXbq4fSFLiNjpBgireOo8xYx8VYNvtyQhY3e9'
access_secret = 'TuSXLzXd9VPRyILFxo9d6QDwPHd4yjFAVEAxfc4kBtRql'


def get_all_tweets(screen_name):
        # Twitter only allows access to a users most recent 3240 tweets with this method
        
        # authorize twitter, initialize tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)
     
        # initialize a list to hold all the tweepy Tweets
        alltweets = []        
        
        # make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = api.user_timeline(screen_name = screen_name,count=199)
        
        # save most recent tweets
        alltweets.extend(new_tweets)
        
        # save the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        # keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
                
                #all subsiquent requests use the max_id param to prevent duplicates
                new_tweets = api.user_timeline(screen_name = screen_name,count=199,max_id=oldest)
                
                #save most recent tweets
                alltweets.extend(new_tweets)
                
                #update the id of the oldest tweet less one
                oldest = alltweets[-1].id - 1

        #print total tweets fetched from given screen name

        print ("Total tweets downloaded from "+str(screen_name)+ " are "+ str(len(alltweets)))
        
        return alltweets

def fetch_tweets(screen_names):

        # initialize the list to hold all tweets from all users
        alltweets=[]

        # get all tweets for each screen name
        for  screen_name in screen_names:
                alltweets.extend(get_all_tweets(screen_name))

        return alltweets

def store_tweets(alltweets,file):

        # a list of all formatted tweets
        tweet_list=[]

        for tweet in alltweets:

                # a dict to contain information about single tweet
                tweet_information=dict()

                # text of tweet
                tweet_information['lang']=tweet.lang
                #print(tweet.text.encode('utf-8'))
                
                
                # text of tweet
                tweet_information['text']=tweet.text
                #print(tweet.text.encode('utf-8'))

                # date and time at which tweet was created
                tweet_information['created_at']=tweet.created_at.strftime("%Y-%m-%d %H:%M:%S")

                # id of this tweet
                tweet_information['id_str']=tweet.id_str

                # retweet count
                tweet_information['retweet_count']=tweet.retweet_count

                # favourites count
                tweet_information['favorite_count']=tweet.favorite_count

                # screename of the user to which it was replied (is Nullable)
                tweet_information['in_reply_to_screen_name']=tweet.in_reply_to_screen_name

                # user information in user dictionery
                user_dictionery=tweet._json['user']

                # no of posts of the user
                tweet_information['statuses_count']=user_dictionery['statuses_count']
                               
                # no of followers of the user
                tweet_information['followers_count']=user_dictionery['friends_count']
                
                # no of friends of the user
                tweet_information['friends_count']=user_dictionery['followers_count']
                         
                # screename of the person who tweeted this
                tweet_information['screen_name']=user_dictionery['screen_name']

                # add this tweet to the tweet_list
                tweet_list.append(tweet_information)
                
        # open file desc to output file with write permissions
        file_des=open(file,'w')
          
        # dump tweets to the file
        for t in tweet_list:
                json.dump(t,file_des,sort_keys=True)
                file_des.write('\n')
        # close the file_des
        file_des.close()


if __name__ == '__main__':
        start_time = time.time()
    
    
        # pass in the username of the account you want to download
        #alltweets=get_all_tweets(sys.argv[1])
        #path= "/home/youcef/Documents/Test2/"+str(sys.argv[1][1:])+"_timeline.json"
        #store_tweets(alltweets,path)
        ids= open ((os.path.join(sys.path[0]+"/Twitter_Fin_accounts2.txt")),'r')
        dir_path=path= os.path.join(sys.path[0]+"/Twitter_Users_timeline2/")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        for line in ids.readlines()[724:]:
            #line=line.split('\t')[0]
            print('##############################')
            print(line)
            try:
                alltweets=get_all_tweets(line)
                file_path= dir_path +str(line).strip('\n')+"_timeline.json"
                store_tweets(alltweets,file_path)        
            except Exception as E1:
                print('User Has no tweets')
                print(E1)
            print('##############################')        
        print("--- %s seconds ---" % (time.time() - start_time))      
                

