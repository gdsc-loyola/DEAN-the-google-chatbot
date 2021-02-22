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

def process_media(media):
    '''How do you process a picture/video lol'''
    pass
    return