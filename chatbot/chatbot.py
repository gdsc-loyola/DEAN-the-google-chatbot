from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, request
from googlesearch import search
import concurrent.futures
import functools
import json
import lxml
import os
from chatbot.pymessenger_updated import Bot
import re
import requests
from threading import Thread
from time import sleep
import time

load_dotenv()

app = Flask(__name__)
ACCESS_TOKEN = os.environ['PAGE_ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)
headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
articles = ''
choice = ''
    
number_of_results = 5 #Number of searches to send
count = 80 #Word count per message

def timeout(seconds_before_timeout):
    """
    Timeout decorator
    """
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, seconds_before_timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(seconds_before_timeout)
            except Exception as e:
                print('error starting thread')
                raise e
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

@timeout(5)
def get_request(url):
    """
    Gets the website and scrapes it using BeautifulSoup
    """
    try:
        page = requests.get(url, headers = headers,timeout=5)
        if page.status_code != 200:
        #Page not loaded, go to the next URL
            return
    except:
        print('Link timed out')
        return
    
    soup = BeautifulSoup(page.content,'lxml')
    return soup
    

def scraper(url:str):
    """
    Scrapes the Link for Text and Formats
    """
    
    global count
    global headers
    
    soup = ''

    #Timeout decorator somewhere here (start)
    try:
        soup = get_request(url)
    except:
        return
    
    #Timeout decorator somewhere here (end)
    
    try:
        title = soup.find_all('title')[0].text.strip() + "\n(Link: " + url + " )\n---\n"
    except:
        return
    
    processed = [i for i in [tag.text.strip() for tag in soup.find_all() if tag.name in ['p']] if i]

    temp = ''' '''.join(processed).replace("\n"," ").replace("\r"," ").split(''' ''')
    article = [''' '''.join(temp[word:word+count]) for word in range(0,len(temp),count)]
    
    if len(article) < 4:
        #Page not loaded, go to the next URL
        return

    my_dict = {'title':title + ''' ''' + article[0][0:450],'article':article}

    return my_dict

def links(keyword:str):
    
    """
    Retrieves the links from the search results.
    """
    results = []
    links = search(keyword, tld='com', num=10, stop=10, pause=2)
    
    #If the search yielded no results
    if not links:
        #The chatbot tells the person to refine their search
        return
    
    for item in links:
        results.append(item)
    
    return results
    
def push(results:list):
    
    """
    Multithreaded scraping 
    """

    global number_of_results

    threads = min(32,len(results))
    new_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        map_object = executor.map(scraper,results)
    for article in map_object:
        if article:
            new_list.append(article)
            if len(new_list) == number_of_results:
                return new_list
    return new_list

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():

    #remember list of articles and what are article the user is reading
    global articles
    global choice

    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")

        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:   
            messaging = event['messaging']
            for message in messaging:
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']

                #If user sent a message
                if message.get('message'):
                    if message['message'].get('text'):
                        string = message['message'].get('text').lstrip().split(' ',1)
                        
                        #If the person wants to search something
                        if string[0].lower() == 'search':
                            send_message(recipient_id,"Thank you for your search! Let me see what I can find. :)")
                            articles = ''
                            articles = push(links(string[1]))
                            if articles:
                                print(articles)
                                for i in range(len(articles)):
                                    
                                    #Send a button allowing them to read more of the article
                                    buttons = [
                                                    {
                                                        "type":"postback",
                                                        "title":"Read",
                                                        "payload": i
                                                    }
                                                ]
                                    #Send the title and summary of the article
                                    button_message(recipient_id,articles[i]['title'][0:600],buttons)
                            else:
                                send_message(recipient_id,'''I couldn't find anything on that, could you try making your search more specific? It would help if you asked a question! (Ex. "Who is the President of the Philippines?)''')
                        else:
                            send_message(recipient_id,"Hey, I'm Dean! I allow Filipinos to access Google Search at no cost. This app runs purely on Free Facebook Data.\nIf you want to get started, just ask me a question! Make sure you write 'search' before your query. I'm excited to learn with you!\nI hope that you continue to stay safe! :)")
                            #sleep(3)
                            #send_message(recipient_id, "If you want to get started, just ask me a question! Make sure you write 'search' before your query. I'm excited to learn with you!")
                            #sleep(3)
                            #send_message(recipient_id, "I hope that you continue to stay safe! :)")
                #If user clicked one of the postback buttons
                elif message.get('postback'):
                    if message['postback'].get('title'):
                        #If user wants to read a specific article
                        if message['postback']['title'] == 'Read':
                            choice = int(message['postback']['payload'])
                            buttons = [
                                            {
                                                "type":"postback",
                                                "title":"Read more",
                                                "payload":choice
                                            }
                                        ]
                            button_message(recipient_id,articles[choice]['article'][0],buttons)
                            if len(articles[choice]['article']) == 1:
                                send_message(recipient_id,articles[choice]['article'][0])
                                articles[choice]['article'] = "End"
                                send_message(recipient_id,"End of Article")
                            elif articles[choice]['article'] == "End":
                                send_message(recipient_id,"End of Article")
                            else:
                                articles[choice]['article'] = articles[choice]['article'][1:]
                        #If user wants to read more of the article
                        elif message['postback']['title'] == 'Read more':
                            buttons = [
                                            {
                                                "type":"postback",
                                                "title":"Read more",
                                                "payload":choice
                                            }
                                        ]
                            button_message(recipient_id, articles[choice]['article'][0], buttons)
                            if len(articles[choice]['article']) == 1:
                                send_message(recipient_id, articles[choice]['article'][0])
                                articles[choice]['article'] = "End"
                                send_message(recipient_id, "End of Article")
                            elif articles[choice]['article'] == "End":
                                send_message(recipient_id, "End of Article")
                            else:
                                articles[choice]['article'] = articles[choice]['article'][1:]
                else:
                    send_message(recipient_id, 'Merry Christmas!')
                
                    #if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        #put something here 
                        pass
    return "Message Processed"

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"    

#uses PyMessenger to send message with button to user
def button_message(recipient_id,response,buttons):
    #sends user the button message provided via input response parameter
    bot.send_button_message(recipient_id,response,buttons)
    return "success"

def timer(func):
    '''Print the Runtime of the decorated function'''
    @functools.wraps(func)
    def wrapper_timer(*args,**kwargs):
        start_time = time.perf_counter()
        value = func(*args,**kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

if __name__ == "__main__":
    app.run()