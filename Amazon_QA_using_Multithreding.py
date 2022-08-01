from bs4 import BeautifulSoup
import requests
import json
import csv
from urllib.parse import urlencode
import time
import concurrent.futures
import datetime
import smtplib
import urllib.request as urllib2
import sys
start_time = time.time()
# asin_list =['B07VT3YDK8']
url = 'https://www.amazon.com/dp/'
# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
API_KEY = 'b5e05b96bcd77d6ea07f376b027e1d69'
NUM_RETRIES = 3
NUM_THREADS = 5
q_and_a_data = []
def q_and_a_extractor(question_url,question_votes):
    params3 = {'api_key': API_KEY, 'url': question_url}
    for _ in range(NUM_RETRIES):
        try:
            link_pages_response = requests.get('http://api.scraperapi.com/', params=urlencode(params3))
            if link_pages_response.status_code in [200, 404]:
                break
        except requests.exceptions.ConnectionError:
            link_pages_response = ''
    if link_pages_response.status_code == 200:
        soup3 = BeautifulSoup(link_pages_response.content, "html.parser")
        answer_l = []
        question = soup3.find("div", {"class": "a-container"}).find("div", {"class": "a-column a-span6"}).find('p').find('span').text
        answers = soup3.find("div", {"class": "a-container"}).find("div", {"class": "a-section a-spacing-large askAnswersAndComments askWrapText"}).find_all("div", {"class": "a-section a-spacing-medium"})
        for ans in answers:
            answer = ans.find('span').text
            answered_by_who = ans.find("div", {"class": "a-row a-spacing-small a-spacing-top-micro"}).find('span').text
            answered_when = ans.find("div", {"class": "a-row a-spacing-small a-spacing-top-micro"}).find('span', {"class": "a-color-tertiary aok-align-center"}).text.replace('\u00b7', ' ').strip()
            answer_helpful = ans.find("div", {"class": "a-row a-spacing-none"}).find('span').text.replace('Do you find this helpful?', ' ').strip()
            anser_dic = {
                "answer": answer,
                "by": answered_by_who.strip(),
                "date": answered_when,
                "helpful": answer_helpful.replace("found this helpful. Do you?", "").strip()
            }
            answer_l.append(anser_dic)
        q_and_a = {"question": question.strip(),
                   "answers": answer_l,
                   "vote": question_votes
                   }
        q_and_a_data.append(q_and_a)
def amazon_q_and_a(asin_number):
    asin_url = url + asin_number
    params = {'api_key': API_KEY, 'url': asin_url}
    for _ in range(NUM_RETRIES):
        try:
            page_response = requests.get('http://api.scraperapi.com/',params=urlencode(params))
            if page_response.status_code in [200, 404]:
                break
        except requests.exceptions.ConnectionError:
            page_response = ''
    if page_response.status_code == 200:
        soup = BeautifulSoup(page_response.content, "html.parser")
        all_Question  = soup.find("div",{"id":"ask_lazy_load_div"}).find("div",{"class":"cdQuestionLazySeeAll"}).find('a').get('href')
        # print(all_Question)
        params1 = {'api_key': API_KEY, 'url': all_Question}
        for _ in range(NUM_RETRIES):
            try:
                page_response1 = requests.get('http://api.scraperapi.com/', params=urlencode(params1))
                if page_response1.status_code in [200, 404]:
                    break
            except requests.exceptions.ConnectionError:
                page_response1 = ''
        if page_response1.status_code == 200:
            soup1 = BeautifulSoup(page_response1.content, "html.parser")
            votes_list = []
            question_link_list = []
            question_last_page = soup1.find("div",{"id":"askPaginationBar"}).find('ul').find_all('li')[-2].find('a').text
            if int(question_last_page) > 10 or int(question_last_page) == 10:
                total_pages = 10 + 1
            else:
                total_pages = int(question_last_page) + 1
            for num in range(1,int(total_pages)):
                question_pages_links = "https://www.amazon.com/ask/questions/asin/"+asin_number+f"/{num}/ref=ask_ql_psf_ql_hza?isAnswered=true"
                params2 = {'api_key': API_KEY, 'url': question_pages_links}
                for _ in range(NUM_RETRIES):
                    try:
                        page_response2 = requests.get('http://api.scraperapi.com/',params=urlencode(params2))
                        if page_response2.status_code in [200, 404]:
                            break
                    except requests.exceptions.ConnectionError:
                        page_response2 = ''
                if page_response2.status_code == 200:
                    soup2 = BeautifulSoup(page_response2.content, "html.parser")
                    question_Links = soup2.find("div",{"class":"a-section askTeaserQuestions"}).find_all("div",{"class":"a-fixed-left-grid a-spacing-base"})
                    for links in question_Links:
                        try:
                            votes = links.find('ul').find("li",{"class":"label"}).find('span').text
                            votes_list.append(votes)
                            question_link ="https://www.amazon.com" + links.find('div',{"class":"a-fixed-left-grid a-spacing-small"}).find('a',{"class":"a-link-normal"}).get('href')
                            question_link_list.append(question_link)
                        except:
                            pass
            votes_list_of_lists = [votes_list[j:j + NUM_THREADS] for j in range(0, len(votes_list), NUM_THREADS)]
            question_link_list_of_lists = [question_link_list[i:i + NUM_THREADS] for i in range(0, len(question_link_list), NUM_THREADS)]
            for u, v in zip(question_link_list_of_lists, votes_list_of_lists):
                with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                    executor.map(q_and_a_extractor, u, v)
    return q_and_a_data

print("--- %s seconds ---" % (time.time() - start_time))