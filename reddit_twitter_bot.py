from datetime import datetime
import os
import praw
import reddit_twitter_config
import requests
import schedule
import tweepy
import time

def reddit_connection():
#Connects to pics subreddit

    #Login to reddit
    reddit = praw.Reddit(client_id = reddit_twitter_config.client_id,
                     client_secret = reddit_twitter_config.client_secret,
                     username = reddit_twitter_config.username,
                     password = reddit_twitter_config.password,
                     user_agent = reddit_twitter_config.user_agent)

    #Return r/pics
    subreddit = reddit.subreddit('pics')
    return subreddit

def fix_title(title):
#Shortens title if too long
    if len(title) < 80:
        return '"' + title + '"'
    else:
        return '"' + title[:79] + '..."'

def get_post_info(subreddit):
    post_dict = {}

    #Use for loop as a generator is returned. Very top most of the day
    for top_pic in subreddit.top('day', limit=1):    

        #Gather post information
        post_dict[top_pic.title] = {}
        post = post_dict[top_pic.title]
        post['score'] = top_pic.score
        post['link'] = top_pic.permalink
        post['img_path'] = store_image(top_pic.url)

    print('Got post from reddit')
    return post_dict

def store_image(img_url):
    if 'redd.it' in img_url or 'imgur' in img_url:
        
        #Make the image folder if not found
        if not os.path.exists('reddit_img'):
            os.makedirs('reddit_img')

        #Create the image path with the date of post
        date = datetime.today().strftime('%d-%m-%Y')    
        img_path = 'reddit_img/' + date + '.jpg'
        
        response = requests.get(img_url)
        if response.status_code == 200: 
            print('Successfully retrieved image page')

            #Create a new file with the img_path name 
            with open(img_path, 'wb') as image_file:
                #Produce the file with the data's content
                image_file.write(response.content)
                
            return img_path
        else: 
            print('Failed to retrieve image page with error: ' + response.status_code)
    else:
        print("Post doesn't point to a redd.it link")
    return ''

def send_tweet(post_dict):
    print ('Logging into Twitter')

    #Login to Twitter
    auth = tweepy.OAuthHandler(reddit_twitter_config.consumer_key,
                               reddit_twitter_config.consumer_secret)
    auth.set_access_token(reddit_twitter_config.access_token,
                          reddit_twitter_config.access_token_secret)
    api = tweepy.API(auth)

    for post in post_dict:

        #Acquire the image path from the stored value in the post dictionary
        img_path = post_dict[post]['img_path']

        #Create associated title post for the reddit post
        score = str(post_dict[post]['score']) + ' Upvotes | '
        text = score + fix_title(post) + ' reddit.com' + post_dict[post]['link']

        #Send Tweet if an image path is found
        if img_path:
            print ('Tweeting text and image')
            api.update_with_media(filename=img_path, status=text)

        #Throw an error if something went wrong as all tweets should have a picture
        else:
            print ('Error: No picture found')
            text_error = 'Error: No picture found'
            api.update_status(status=text_error)

def task():

    subreddit = reddit_connection()
    post_dict = get_post_info(subreddit)
    send_tweet(post_dict)
    
def main():

    #Schedule script to run once a day at 11:59p Eastern Time
    schedule.every().monday.at("22:59").do(task)
    schedule.every().tuesday.at("22:59").do(task)
    schedule.every().wednesday.at("22:59").do(task)
    schedule.every().thursday.at("22:59").do(task)
    schedule.every().friday.at("22:59").do(task)
    schedule.every().saturday.at("22:59").do(task)
    schedule.every().sunday.at("22:59").do(task)

    while True:
        schedule.run_pending()
        time.sleep(1)
    
if __name__ == '__main__':
    main()








		
