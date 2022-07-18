from bs4 import BeautifulSoup
import requests
import json
import csv
from urllib.parse import urlencode
import time
import datetime
import smtplib
import urllib.request as urllib2
import sys
start_time = time.time()
asin_list =['B07VT3YDK8']#,'B08FX35S7K']
url = 'https://www.amazon.com/dp/'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
# with open("category_wise_asin.csv",newline='') as f:
#     ereader = csv.DictReader(f)
#     for row in ereader:
#         asin_list.append(row['asin'])
for number in asin_list:
    asin_url = url + number
    # print(asin_url)
    params = {'api_key': 'e7c4988314b6f4e57c03d0d80c8a68f6', 'url': asin_url}
    page = requests.get('http://api.scraperapi.com/', headers=headers,params=urlencode(params))
    soup = BeautifulSoup(page.content, "html.parser")
    all_Question  = soup.find("div",{"id":"ask_lazy_load_div"}).find("div",{"class":"cdQuestionLazySeeAll"}).find('a').get('href')
    # print(all_Question)
    params1 = {'api_key': 'e7c4988314b6f4e57c03d0d80c8a68f6', 'url': all_Question}
    page1 = requests.get('http://api.scraperapi.com/', headers=headers, params=urlencode(params1))
    soup1 = BeautifulSoup(page1.content, "html.parser")
    question_last_page = soup1.find("div",{"id":"askPaginationBar"}).find('ul').find_all('li')[-2].find('a').text
    # print(question_last_page)
    for num in range(1,11):
        question_pages_links = "https://www.amazon.com/ask/questions/asin/"+number+f"/{num}/ref=ask_ql_psf_ql_hza?isAnswered=true"
        print(question_pages_links)
        params2 = {'api_key': 'e7c4988314b6f4e57c03d0d80c8a68f6', 'url': question_pages_links}
        page2 = requests.get('http://api.scraperapi.com/', headers=headers, params=urlencode(params2))
        soup2 = BeautifulSoup(page1.content, "html.parser")
        question_Links = soup2.find("div",{"class":"a-section askTeaserQuestions"}).find_all("div",{"class":"a-fixed-left-grid a-spacing-base"})
        # print(question_Link)
        for links in question_Links:
            try:
                votes = links.find('ul').find("li",{"class":"label"}).find('span').text
                question_link ="https://www.amazon.com" + links.find('div',{"class":"a-fixed-left-grid a-spacing-small"}).find('a',{"class":"a-link-normal"}).get('href')
                params3 = {'api_key': 'e7c4988314b6f4e57c03d0d80c8a68f6', 'url': question_link}
                page3 = requests.get('http://api.scraperapi.com/', headers=headers, params=urlencode(params3))
                soup3 = BeautifulSoup(page3.content, "html.parser")
                answer_l=[]
                question = soup3.find("div",{"class":"a-container"}).find("div",{"class":"a-column a-span6"}).find('p').find('span').text
                answers = soup3.find("div",{"class":"a-container"}).find("div",{"class":"a-section a-spacing-large askAnswersAndComments askWrapText"}).find_all("div",{"class":"a-section a-spacing-medium"})
                for ans in answers:
                    answer = ans.find('span').text
                    answered_by_who = ans.find("div",{"class":"a-row a-spacing-small a-spacing-top-micro"}).find('span').text
                    answered_when = ans.find("div", {"class": "a-row a-spacing-small a-spacing-top-micro"}).find('span',{"class":"a-color-tertiary aok-align-center"}).text.replace('.',' ').strip()
                    answer_helpful = ans.find("div", {"class": "a-row a-spacing-none"}).find('span').text.replace('Do you find this helpful?',' ').strip()
                    anser_dic = {
                        "answer": answer,
                        "by": answered_by_who.strip(),
                        "date": answered_when,
                        "helpful": answer_helpful.replace("found this helpful. Do you?", "").strip()
                    }
                    answer_l.append(anser_dic)
                q_and_a = {"question": question.strip(),
                           "answers": answer_l,
                           "vote": votes
                           }
                print(q_and_a)
            except:
                pass