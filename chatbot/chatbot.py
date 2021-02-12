from chatbot.conversation import process_message, process_media, search
from chatbot.pymessenger_updated import Bot
from dotenv import load_dotenv
from flask import Flask, request
import functools
import json
import os
import random
import re
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
        search(df, message_dict, initial_message, message_dict)

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