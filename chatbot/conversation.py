import re

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

def evaluate(message):
    status = ""

    #If POST request is a message
    if message.get("message"):
        if message["message"].get("text"):
            text = message['message'].get('text').strip()
            string = text.lstrip().split(' ',1)

            #Checks for valid searches
            if string[0].lower() == "search" and len(string) >= 2:
                status = "valid"
            else:
                status = "invalid"
        elif message["message"].get("attachment"):
            status = "attachment"
            
    #If POST request is a postback
    elif message.get("postback"):
        if message["postback"].get("title"):
            if message["postback"]["title"] == "Get Started":
                status = "get started"
            elif message["postback"]["title"] == "Read":
                status = "read"
            elif message["postback"]["title"] == "Read more":
                status = "read more"
            elif message["postback"]["title"] == "Search more":
                status = "search more"
    return status

def process_media(media):
    '''How do you process a picture/video lol'''
    pass
    return