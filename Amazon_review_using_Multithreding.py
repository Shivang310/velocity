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
API_KEY = 'b5e05b96bcd77d6ea07f376b027e1d69'
NUM_RETRIES = 3
NUM_THREADS = 5
# asin_list =['B07VT3YDK8']
url = 'https://www.amazon.com/dp/'
# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
data_reviews = []
def extractor(review_page_link):
    try:
        params3 = {'api_key': API_KEY, 'url': review_page_link}
        for _ in range(NUM_RETRIES):
            try:
                link_pages_response = requests.get('http://api.scraperapi.com/',params=urlencode(params3))
                if link_pages_response.status_code in [200, 404]:
                    break
            except requests.exceptions.ConnectionError:
                link_pages_response = ''
        if link_pages_response.status_code == 200:
            soup3 = BeautifulSoup(link_pages_response.content, "html.parser")
            total_reviews = soup3.find("div",{"id":"cm_cr-review_list"}).find_all("div",{"class":"a-section review aok-relative"})
            for diff in total_reviews:
                try:
                    try:
                        reviewer_name = diff.find('span',{"class":"a-profile-name"}).text
                    except:
                        reviewer_name = ''
                    try:
                        rev_prof_url ='https://www.amazon.com' + diff.find('a').get('href')
                    except:
                        rev_prof_url = ''
                    try:
                        star_Rating = diff.find_all('span')[1].text
                    except:
                        star_Rating = ''
                    try:
                        review_heading = diff.find('a',{"data-hook":"review-title"}).find('span').text.strip()
                    except:
                        review_heading = ''
                    try:
                        review_date = diff.find('span',{"data-hook":"review-date"}).text.replace("Reviewed in the United States on "," ").strip()
                    except:
                        review_date = ''
                    try:
                        review_body = diff.find('span',{"data-hook":"review-body"}).find('span').text.strip()
                    except:
                        review_body = ''
                    try:
                        helpful = diff.find('span',{"data-hook":"helpful-vote-statement"}).text.strip()
                    except:
                        helpful = ''
                    product_reviews = {"reviewerName": reviewer_name,
                                       "reviewerUrl": rev_prof_url,
                                       "rating": star_Rating,
                                       "reviewTitle": review_heading,
                                       "reviewDate": review_date,
                                       "reviewText": review_body,
                                       "is_Helpful": helpful}
                    data_reviews.append(product_reviews)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)
def amazon_review(asin_number):
    asin_url = url + asin_number
    params = {'api_key': API_KEY, 'url': asin_url}
    review_pages_links = []
    for _ in range(NUM_RETRIES):
        try:
            page_response = requests.get('http://api.scraperapi.com/',params=urlencode(params))
            if page_response.status_code in [200, 404]:
                break
        except requests.exceptions.ConnectionError:
            page_response = ''
    if page_response.status_code == 200:
        soup1 = BeautifulSoup(page_response.text, "html.parser")
        try:
            total_review_link = 'https://www.amazon.com' +soup1.find("div",{"id":"reviews-medley-footer"}).find('a').get('href')
            review_pages_links.append(total_review_link)
            params2 = {'api_key': API_KEY, 'url': total_review_link}
            for _ in range(NUM_RETRIES):
                try:
                    review_pages_response = requests.get('http://api.scraperapi.com/',params=urlencode(params2))
                    if review_pages_response.status_code in [200, 404]:
                        break
                except requests.exceptions.ConnectionError:
                    review_pages_response = ''
            review_pages = requests.get('http://api.scraperapi.com/',params=urlencode(params2))
            if review_pages_response.status_code == 200:
                soup2 = BeautifulSoup(review_pages_response.text, "html.parser")
                total_number_of_reviews = soup2.find("div",{"id":"filter-info-section"}).text.strip().split('total ratings,')[1].replace(' with reviews','').strip()
                if ',' in total_number_of_reviews:
                    number_of_review = "".join(total_number_of_reviews.split(','))
                    total_number = number_of_review
                else:
                    total_number = total_number_of_reviews
                number_of_pages = int(total_number)/10
                if number_of_pages > 100 or number_of_pages == 100:
                    total_number_page = 100 + 1
                else:
                    total_number_page = number_of_pages + 1
                for page_no in range(2,int(total_number_page)):
                    next_page_link = "https://www.amazon.com/product-reviews/"+asin_number+f"/ref=cm_cr_arp_d_paging_btm_next_{page_no}?ie=UTF8&pageNumber={page_no}"
                    review_pages_links.append(next_page_link)
        except Exception as e:
            print(e)
    review_pages_links_list_of_lists = [review_pages_links[i:i + NUM_THREADS] for i in range(0, len(review_pages_links), NUM_THREADS)]
    for review_url in review_pages_links_list_of_lists:
         with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                executor.map(extractor, review_url)
    return data_reviews
print("--- %s seconds ---" % (time.time() - start_time))