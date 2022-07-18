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
asin_list =['B07VT3YDK8','B07K2676W7','B08FCV5YWP','B098RKWHHZ','B00Z0UWV98']
url = 'https://www.amazon.com/dp/'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
# with open("category_wise_asin.csv",newline='') as f:
#     ereader = csv.DictReader(f)
#     for row in ereader:
#         asin_list.append(row['asin'])
def extractor(review_page_link):
    try:
        print(review_page_link)
        params3 = {'api_key': '6874620ab92abd457c56d814fac10066', 'url': review_page_link}
        link_pages_response = requests.get('http://api.scraperapi.com/', headers=headers,params=urlencode(params3))
        soup3 = BeautifulSoup(link_pages_response.content, "html.parser")
        total_reviews = soup3.find("div",{"id":"cm_cr-review_list"}).find_all("div",{"class":"a-section review aok-relative"})
        # print(total_reviews)
        for diff in total_reviews:
            try:
                reviewer_name = diff.find_all('span')[0].text
                print(reviewer_name)
                rev_prof_url ='https://www.amazon.com' + diff.find('a').get('href')
                print(rev_prof_url)
                star_Rating = diff.find_all('span')[1].text
                print(star_Rating)
                review_heading = diff.find_all('span')[3].text
                print(review_heading)
                review_date = diff.find_all('span')[4].text.replace("Reviewed in the United States on "," ").strip()
                print(review_date)
                review_body = diff.find_all('span')[6].text.strip()
                print(review_body)
                try:
                    helpful = diff.find_all('span')[8].text.strip().replace("Helpful"," ")
                    print(helpful)
                except:
                    pass
            except:
                pass
    except Exception as e:
        print(e)
for number in asin_list:
    asin_url = url + number
    params = {'api_key': '6874620ab92abd457c56d814fac10066', 'url': asin_url}
    page = requests.get('http://api.scraperapi.com/', headers=headers,params=urlencode(params))
    soup1 = BeautifulSoup(page.content, "html.parser")
    try:
        total_review_link = 'https://www.amazon.com' +soup1.find("div",{"id":"reviews-medley-footer"}).find('a').get('href')
        extractor(total_review_link)
        params2 = {'api_key': '6874620ab92abd457c56d814fac10066', 'url': total_review_link}
        review_pages = requests.get('http://api.scraperapi.com/', headers=headers,params=urlencode(params2))
        soup2 = BeautifulSoup(review_pages.content, "html.parser")
        # total_number_of_reviews = soup2.find("div",{"id":"filter-info-section"}).text.strip().split('total ratings,')[1].replace(' with reviews','').strip()
        # # print(total_number_of_reviews)
        # if ',' in total_number_of_reviews:
        #     number_of_review = "".join(total_number_of_reviews.split(','))
        #     total_number = number_of_review
        # else:
        #     total_number = total_number_of_reviews
        # number_of_pages = int(total_number)/10
        # # print(number_of_pages)
        # if isinstance(number_of_pages, float):
        #     total_number = int(number_of_pages)+2
        # else:
        #     total_number = number_of_pages+1
        for page_no in range(2,101):
            next_page_link = "https://www.amazon.com/product-reviews/"+number+f"/ref=cm_cr_arp_d_paging_btm_next_{page_no}?ie=UTF8&pageNumber={page_no}"
            extractor(next_page_link)
    except Exception as e:
        print(e)

print("--- %s seconds ---" % (time.time() - start_time))