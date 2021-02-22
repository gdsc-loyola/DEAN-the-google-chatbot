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
    elif text == 'ajma':
        answer = "Need more time to decide on which Pool to join? 🤔 Good news!\n\nThe application period for Training Pools Phase 2 has been extended. Join our learning community and develop your skills with us.\n\nThe extended deadline for applications is on February 25, 2021 (Thursday), at 11:59PM.\n\nApply while slots last: tinyurl.com/TrainingPoolsPhase2\n\nRead through the primer here: tinyurl.com/TrainingPools2021Primer\n\nWe can’t wait to learn with you! 🤗"
        return answer
    elif text == 'red':
        answer = "If you're interested in learning more about marketing, please react to this comment as well, so we can add you to a group chat for mkt lectures <3 c/o the champ Red Nadela"
        return answer
    elif text == 'sv':
        answer = "Find your connection this Valentine’s Day in AJMA Secret Valentine’s Speed Dating Event on February 14, 2021, at 8:30PM via Zoom.\n\nEveryone is invited to join us as we celebrate Heart’s Day together <3\n\nZoom link: https://tinyurl.com/AJMASecretValentineSpeedDating"
        return answer
    elif text == 'chanti':
        answer = "DOPEEEEEEEEEEEEEEEEEEEEEEEEE SKSKSKSKSK"
        return answer
    return answer

def process_media(media):
    '''How do you process a picture/video lol'''
    pass
    return