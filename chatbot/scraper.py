import concurrent.futures
from bs4 import BeautifulSoup
from flask import request
import requests
from threading import Thread
from googlesearch import search
import lxml
import functools

headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
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

@timeout(15)
def get_request(url):
    """
    Gets the website and scrapes it using BeautifulSoup
    """
    try:
        page = requests.get(url, headers = headers,timeout=10)
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
        uid = soup.find_all('title')[0].text.strip()
        title = uid + "\n(Link: " + url + " )\n---\n"
         
    except:
        return
    
    processed = [i for i in [tag.text.strip() for tag in soup.find_all() if tag.name in ['p']] if i]

    temp = ''' '''.join(processed).replace("\n"," ").replace("\r"," ").split(''' ''')
    article = [''' '''.join(temp[word:word+count]) for word in range(0,len(temp),count)]
    
    if len(article) < 4:
        #Page not loaded, go to the next URL
        return

    my_dict = {'uid':uid,'title':title + ''' ''' + article[0][0:450],'article':article}

    return my_dict

def links(keyword:str):
    
    """
    Retrieves the links from the search results.
    """
    results = []
    links = search(keyword, num=10, stop=10, pause=2)
    
    #If the search yielded no results
    if not links:
        #The chatbot tells the person to refine their search
        return
    
    #Remove duplicate links
    [results.append(link) for link in links if link not in results]
    
    return results
    
def push(results:list):
    
    """
    Multithreaded scraping 
    """

    global number_of_results

    threads = min(32,len(results))
    new_list = []
    titles = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        map_object = executor.map(scraper,results)
    for article in map_object:
        if article and (article['uid'] not in titles):
            new_list.append(article)
            titles.append(article['uid'])
            if len(new_list) == number_of_results:
                return new_list
    return new_list