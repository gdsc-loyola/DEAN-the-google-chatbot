from chatbot.conversation import process_message, process_media
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
        if os.path.exists('df.pickle'):
            with open('df.pickle', 'rb') as x:
                df = pickle.load(x)

        with open('message.pickle', 'wb') as x:
            pickle.dump(message_dict, x, protocol=pickle.HIGHEST_PROTOCOL)

        # Get POST request sent to the bot
        output = request.get_json()
        print(output)

        # Get message details
        message = output['entry'][0]['messaging'][0]

        #Facebook Messenger ID for user so we know where to send response back to
        recipient_id = str(message['sender']['id'])
        message_dict[recipient_id] = message

        #If user sent a message
        if message.get('message'):
            if message['message'].get('text'):
                text = message['message'].get('text').strip()
                string = text.lstrip().split(' ',1)
                
                #If the person wants to search something
                if string[0].lower() == 'search' and len(string) >= 2:

                    #Stops message spam
                    with open('message.pickle', 'rb') as x:
                        previous_message = pickle.load(x)
                        check_message = previous_message

                    #Store recipient ID in previous message
                    if check_message.get(recipient_id):
                        pass
                    else:
                        initial_message[recipient_id] = {}
                        previous_message = initial_message

                    print('previous message: ', previous_message[recipient_id])
                    print('message: ', message)
                    if message == previous_message[recipient_id]:
                        print('STOP FUNCTION BEFORE IT SPAMS')
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
                            
                        else:
                            send_message(recipient_id,'''I couldn't find anything on that, could you try making your search more specific? It would help if you asked a question! (Ex. "Who is the President of the Philippines?)''')
                    return "Messaged Processed"
                #If the person mistakenly just said search
                elif string[0].lower() == 'search' and len(string) == 1:
                    send_message(recipient_id, "Hi there! Make sure that you type 'search' before your question. Ex. search Who is the President of the Philippines?")
                    #TELL THEM THAT 
                #All other cases 
                else:
                    answer = process_message(text)
                    if answer:
                        send_message(recipient_id,answer)
                    else:
                        send_message(recipient_id,"Can you say that again? Make sure that you type 'search' before your question. Ex. search Who is the President of the Philippines?")
                return "Messaged Processed"
            #if user sends us a GIF, photo,video, or any other non-text item
            if message['message'].get('attachments'):
                #process_media(message['message'].get('attachments'))
                pass
                return "Messaged Processed"
        #If user clicked one of the postback buttons
        elif message.get('postback'):
            print('DF Keys Existing: ',df.keys())
            if message['postback'].get('title'):
                #If user clicks the get started button
                if message['postback']['title'] == 'Get Started':
                    send_message(recipient_id, "Hey, I'm Dean! I allow Filipinos to access Google Search at no cost. This app runs purely on Free Facebook Data.\n\nIf you want to get started, just ask me a question! Make sure you write 'search' before your query. I'm excited to learn with you!\n\nI hope that you continue to stay safe! :)")
                
                #If user wants to read a specific article
                #update df with new choice
                elif df.get(recipient_id):
                    #retrieve choice from postback
                    choice = int(message['postback']['payload'])
                    df[recipient_id][0] = choice
                    if message['postback']['title'] == 'Read':
                        print('DF Keys Read: ',df.keys())
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
                    elif message['postback']['title'] == 'Read more':
                        buttons = [
                                        {
                                            "type":"postback",
                                            "title":"Read more",
                                            "payload":choice
                                        }
                                    ]
                        print('Read More Keys: ',df.keys())
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
                    elif message['postback']['title'] == 'Feedback':
                        pass
                else:
                    send_message(recipient_id, "Hi there! Could you please repeat your search? Make sure you write 'search' before your query. Ex. search Who is the President of the Philippines")
                return "Messaged Processed"
        else:
            #gets triggered if there is another type of message that's not message/postback
            pass
    return "Message processed"

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