def process_message(text):
    '''Understand what they said'''
    answer = ''
    greetings = ['hi','hello']

    if text.lower() in greetings:
        answer = 'Hello there!'
    return answer