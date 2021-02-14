from chatbot.conversation import process_message, process_media, evaluate
from chatbot.scraper import push, links, scraper, get_request, timeout
from chatbot.pymessenger_updated import Bot
from dotenv import load_dotenv
from flask import Flask, request
import functools
import json
import os
import random
import re
import pickle
import time

load_dotenv()

app = Flask(__name__)
ACCESS_TOKEN = os.environ['PAGE_ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)
df = {}
message_dict = {}
initial_message = {}

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    #remember list of articles and what are article the user is reading
    global df
    global message_dict
    global initial_message

    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")

        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        #Load df
        if os.path.exists('df.pickle'):
            with open('df.pickle', 'rb') as x:
                df = pickle.load(x)

        #Make pickle file for previou message
        with open('message.pickle', 'wb') as x:
            pickle.dump(message_dict, x, protocol=pickle.HIGHEST_PROTOCOL)

        # Get POST request sent to the bot
        output = request.get_json()

        # Get message details
        message = output['entry'][0]['messaging'][0]

        #Facebook Messenger ID for user so we know where to send response back to
        recipient_id = str(message['sender']['id'])
        message_dict[recipient_id] = message

        #If search is valid
        if evaluate(message) == "valid":
            text = message['message'].get('text').strip()
            string = text.lstrip().split(' ',1)
            
            #Handles previous message
            with open('message.pickle', 'rb') as x:
                previous_message = pickle.load(x)
                check_message = previous_message

            #Handles initial message
            if check_message.get(recipient_id):
                pass
            else:
                initial_message[recipient_id] = {}
                previous_message = initial_message

            if message == previous_message[recipient_id]:
                return 'message processed'
            else: 
                send_message(recipient_id,"Thank you for your search! Let me see what I can find. :)")
                articles = push(links(string[1]))
                if articles:
                    df.pop(recipient_id, None)
                    with open('df.pickle', 'wb') as x:
                        pickle.dump(df, x, protocol=pickle.HIGHEST_PROTOCOL)
                    articles.insert(0,1)
                    df[recipient_id] = articles
                    with open('df.pickle', 'wb') as z:
                        pickle.dump(df, z, protocol = pickle.HIGHEST_PROTOCOL)
                    #feedback(recipient_id)
                    for i in range(1,len(articles)):
                        #Send a button allowing them to read more of the article
                        buttons = [
                                        {
                                            "type":"postback",
                                            "title":"Read",
                                            "payload": i
                                        }
                                    ]
                        #Send the title and summary of the article
                        button_message(recipient_id,articles[i]['title'][0:350],buttons)
                    search_more = [
                        {
                            "type":"postback",
                            "title":"Search more",
                            "payload":"Search more"
                        }
                    ]
                    button_message(recipient_id, "Search more articles!", search_more)
                    return "Messaged Processed"

        #If search is invalid
        elif evaluate(message) == "invalid":
            answer = process_message(message['message'].get('text').strip())
            if answer:
                send_message(recipient_id, answer)
            else:
                send_message(recipient_id, "Can you say that again? Make sure that you type 'search' before your question. Ex. search Who is the President of the Philippines?")

            return "Messaged Processed"

        #if user sends us a GIF, photo,video, or any other non-text item
        elif evaluate(message) == "attachment":
                #process_media(message['message'].get('attachments'))
                pass
                return "Messaged Processed"

        #If user clicked the get started button
        elif evaluate(message) == "get started":
            send_message(recipient_id, "Hey, I'm Dean! I allow Filipinos to access Google Search at no cost. This app runs purely on Free Facebook Data.\n\nIf you want to get started, just ask me a question! Make sure you write 'search' before your query. I'm excited to learn with you!\n\nI hope that you continue to stay safe! :)")
        
        #If user wants to browse more articles
        elif evaluate(message) == "search more":
            send_message(recipient_id, "Searching for more articles please wait a moment")
            articles = search_more(string[1], articles)

            df.pop(recipient_id, None)
            with open('df.pickle', 'wb') as x:
                pickle.dump(df, x, protocol=pickle.HIGHEST_PROTOCOL)
            articles.insert(0,1)
            df[recipient_id] = articles
            with open('df.pickle', 'wb') as z:
                pickle.dump(df, z, protocol = pickle.HIGHEST_PROTOCOL)

            for i in range(1,len(articles)):
                #Send a button allowing them to read more of the article
                buttons = [
                                {
                                    "type":"postback",
                                    "title":"Read",
                                    "payload": i
                                }
                            ]
                #Send the title and summary of the article
                button_message(recipient_id,articles[i]['title'][0:350],buttons)


        #If user wants to read a specific article
        elif evaluate(message) == "read":
            #retrieve choice from postback
            choice = int(message['postback']['payload'])

            #update df with new choice
            df[recipient_id][0] = choice

            #dictionary for buttons
            buttons = [
                            {
                                "type":"postback",
                                "title":"Read more",
                                "payload":choice
                            }
                        ]
            #send button message
            if len(df[recipient_id][choice]['article']) == 1:
                send_message(recipient_id,df[recipient_id][choice]['article'][0])
                df[recipient_id][choice]['article'] = "End"
                with open('df.pickle', 'wb') as x:
                    pickle.dump(df, x, protocol=pickle.HIGHEST_PROTOCOL)
                send_message(recipient_id,"End of Article")
            elif df[recipient_id][choice]['article'] == "End":
                send_message(recipient_id,"End of Article")
            else:
                button_message(recipient_id,df[recipient_id][choice]['article'][0],buttons)
                df[recipient_id][choice]['article'] = df[recipient_id][choice]['article'][1:]
                with open('df.pickle', 'wb') as x:
                    pickle.dump(df, x, protocol=pickle.HIGHEST_PROTOCOL)
            return "Messaged Processed"

        #If user wants to read more of the article
        elif evaluate(message) == 'read more':
            buttons = [
                            {
                                "type":"postback",
                                "title":"Read more",
                                "payload":choice
                            }
                        ]
            if len(df[recipient_id][choice]['article']) == 1:
                send_message(recipient_id, df[recipient_id][choice]['article'][0])
                df[recipient_id][choice]['article'] = "End"
                with open('df.pickle', 'wb') as x:
                    pickle.dump(df, x, protocol=pickle.HIGHEST_PROTOCOL)
                send_message(recipient_id, "End of Article")
            elif df[recipient_id][choice]['article'] == "End":
                send_message(recipient_id, "End of Article")
            else:
                button_message(recipient_id, df[recipient_id][choice]['article'][0], buttons)
                df[recipient_id][choice]['article'] = df[recipient_id][choice]['article'][1:]
                with open('df.pickle', 'wb') as x:
                    pickle.dump(df, x, protocol=pickle.HIGHEST_PROTOCOL)
            return "Messaged Processed"

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'    

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    '''sends user the text message provided via input response parameter'''
    bot.send_text_message(recipient_id, response)
    return "success"

#uses PyMessenger to send message with button to user
def button_message(recipient_id,response,buttons):
    '''sends user the button message provided via input response parameter'''
    bot.send_button_message(recipient_id,response,buttons)
    return "success"

def feedback(recipient_id):
    '''Send a feedback button to let them provide feedback'''
    if random.random() <= 0.3:
        time.sleep(1.5)
        message = 'Thank you for using DEAN! If you have any comments or suggestions, let us know here! :)'
        buttons = [
                        {
                            "type":"postback",
                            "title":"Feedback",
                            "payload":recipient_id
                        }
                    ]
        button_message(recipient_id,message,buttons)
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