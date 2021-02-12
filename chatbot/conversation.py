from chatbot.pymessenger_updated import Bot
from chatbot.scraper import timeout, get_request, scraper, links, push
from flask import request
import re
import pickle
import os

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

def process_message(text):
    '''Understand what they said'''
    text = text.lower().strip()
    answer = ''

    #match
    greetings = ['hi','hello']
    gratitude = 'thank'

    if any(re.search(re.compile(f'\\b{x}\\b'),text) for x in greetings):
        answer = "Hello there!"
        return answer
    elif re.search(gratitude,text):
        answer = "You're welcome! :)"
        return answer
    elif text == 'read':
        answer = "I'm sorry I did not understand that. Please click the read button rather than typing it. :)"
        return answer
    elif text == 'read more':
        answer = "I'm sorry I did not understand that. Please click the read more button rather than typing it. :)"
        return answer

    return answer

def search(df, message, initial_message, message_dict):
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

def process_media(media):
    '''How do you process a picture/video lol'''
    pass
    return