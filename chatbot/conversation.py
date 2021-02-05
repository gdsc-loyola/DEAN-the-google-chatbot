def process_message(text):
    '''Understand what they said'''
    answer = ''
    greetings = ['hi','hello']

    if text.lower() in greetings:
        answer = 'Hello there!'
    return answer

def process_media(media):
    '''How do you process a picture/video lol'''
    pass
    return