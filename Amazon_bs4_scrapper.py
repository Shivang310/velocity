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
from Amazon_review_using_Multithreding import amazon_review
from Amazon_QA_using_Multithreding import amazon_q_and_a
start_time = time.time()
API_KEY = 'b5e05b96bcd77d6ea07f376b027e1d69'
NUM_RETRIES = 3
NUM_THREADS = 5
asin_list =['B00GB85JR4','B07K2676W7']#,'B08FCV5YWP','B098RKWHHZ','B00Z0UWV98']
base_url = 'https://www.amazon.com/dp/'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
data_reviews = []

# with open("category_wise_asin.csv",newline='') as f:
#     ereader = csv.DictReader(f)
#     for row in ereader:
#         asin_list.append(row['asin'])
class amazon_scraper:
    def __init__(self,product_soup, asin_no):
        self.product_soup = product_soup
        self.asin_no = asin_no
    def amazon_feature(self):
        amazon_features_list = []
        try:
            features = self.product_soup.find("div", {"id": "feature-bullets"}).find('ul').find_all('li')
            # print(features)
            for feat in features:
                amazon_features = feat.text
                amazon_features_list.append(amazon_features)
                # print(amazon_features)
        except:
            pass
        return amazon_features_list
    def amazon_description(self):
        try:
            product_discription = self.product_soup.find("div", {"id": "productDescription"}).find('p').text
            # print(product_discription)
        except:
            product_discription = ''
        return product_discription
    def amazon_breadcrumb(self):
        try:
            breadcrumbs = self.product_soup.find("div", {"id": "wayfinding-breadcrumbs_container"}).find("ul", {"class": "a-unordered-list a-horizontal a-size-small"}).find_all('li')
            product_breadcrumbs = ""
            for bread in breadcrumbs:
                product_breadcrumbs = product_breadcrumbs + bread.text.strip()
            # print(product_breadcrumbs)
            breadcrumb_val = {
                "breadcrumb": product_breadcrumbs
            }
        except Exception as e:
            breadcrumb_val = {
                "breadcrumb": ''
            }
        return breadcrumb_val
    def amazon_product_details(self):
        product_title = self.product_soup.find(id='productTitle').get_text().strip()
        try:
            rating = self.product_soup.find("div", {"id": "reviewsMedley"}).find("span", {"data-hook": "rating-out-of-text"}).text.replace("out of 5", '').strip()
        except:
            try:
                rating = self.product_soup.find("div", {"id": "averageCustomerReviews_feature_div"}).find("span", {"id": "acrPopover"}).find('i').find('span').text.replace("out of 5", '').strip()
            except:
                rating = ''
        try:
            global_ratings = self.product_soup.find("div", {"id": "reviewsMedley"}).find("div", {"data-hook": "total-review-count"}).find('span').text.replace(" global ratings", '').strip()
        except:
            try:
                global_ratings = self.product_soup.find("div", {"id": "averageCustomerReviews_feature_div"}).find("span", {"id": "acrCustomerReviewText"}).text.replace(" ratings", '').strip()
            except:
                global_ratings = ''
        try:
            date_availablity =self.product_soup.find("div", {"id": "detailBullets_feature_div"}).find('ul').find_all('li')[3].find("span", {"class": "a-list-item"}).text.split(":")[1].replace("\u200e\n"," ").strip()
        except:
            date_availablity =''
        try:
            manufacturer = self.product_soup.find("div", {"id": "detailBullets_feature_div"}).find('ul').find_all('li')[4].find("span",{"class": "a-list-item"}).text.split(":")[1].replace("\u200e\n"," ").strip()
        except:
            try:
                manufacturer = self.product_soup.find("div", {"id": "detailBullets_feature_div"}).find('a').text.strip()
            except:
                manufacturer = ''
        try:
            current_price = self.product_soup.find("div", {"id": "apex_desktop_snsAccordionRowMiddle"}).find('span', {"id": "sns-base-price"}).text.strip()
        except:
            try:
                current_price = self.product_soup.find("div", {"id": "corePriceDisplay_desktop_feature_div"}).find('span', {"class": "a-offscreen"}).text.strip()
            except:
                current_price = ''
        try:
            amazon_choice = self.product_soup.find("div", {"id": "acBadge_feature_div"}).find('span', {"class": "a-declarative"}).text
            ac = True
        except:
            ac = False
        try:
            bestseller = self.product_soup.find("div", {"id": "zeitgeistBadge_feature_div"}).find('i', {"class": "a-icon a-icon-addon p13n-best-seller-badge"}).text
            bs = True
        except:
            bs = False
        product_detail = {
            "productURL": base_url + self.asin_no,
            "ASIN": self.asin_no,
            "title": product_title +" ; "+manufacturer,
            'date_first_available': date_availablity,
            "manufacturer": manufacturer,
            "currentPrice": current_price,
            "rating": rating,
            "totalRatings": global_ratings,
            'amazon_choice': ac,
            'best_seller': bs,
            'free_delivery': False,
            'amazon_deleted': False
        }
        return product_detail
if __name__ == "__main__":
    for number in asin_list:
        asin_urls = base_url + number
        # print(asin_urls)
        params = {'api_key': API_KEY, 'url': asin_urls}
        for _ in range(NUM_RETRIES):
            try:
                page_response = requests.get('http://api.scraperapi.com/', params=urlencode(params))
                if page_response.status_code in [200, 404]:
                    print(page_response.status_code)
                    break
            except requests.exceptions.ConnectionError:
                page_response = ''
        if page_response.status_code == 200:
            data = {}
            data['features'] = []
            data['reviewsAspects'] = []
            data['productInformation'] = []
            data['productDescription'] = []
            data['reviews'] = []
            data['qAndA'] = []
            data['time'] = []
            data['reviewsCountInfo'] = []
            data['scrapperInfo'] = []
            data['breadcrumb'] = []
            soup1 = BeautifulSoup(page_response.text, "html.parser")
            product_soup = amazon_scraper(soup1,number)
            product_feature = product_soup.amazon_feature()
            data['features'].append(product_feature)
            product_description = product_soup.amazon_description()
            data['productDescription'].append(product_description)
            product_reviews = amazon_review(number)
            data['reviews'].append(product_reviews)
            product_q_and_a = amazon_q_and_a(number)
            data['qAndA'].append(product_q_and_a)
            product_breadcrumb = product_soup.amazon_breadcrumb()
            data['breadcrumb'].append(product_breadcrumb)
            product_basic_detail = product_soup.amazon_product_details()
            data.update(product_basic_detail)
            # print(data)
            with open(number + ".json", "w") as outfile:
                json.dump(data, outfile)
print("--- %s seconds ---" % (time.time() - start_time))

