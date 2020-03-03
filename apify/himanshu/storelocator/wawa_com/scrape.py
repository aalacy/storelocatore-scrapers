import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import requests
from random import choice
import http.client
import re
import json
import sgzip
import ssl
import urllib3
import pprint
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import platform

system = platform.system()
session = SgRequests()
requests.packages.urllib3.disable_warnings() 
import urllib3

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    if "linux" in system.lower():
        return webdriver.Firefox(executable_path='./geckodriver', options=options)        
    else:
        return webdriver.Firefox(executable_path='geckodriver.exe', options=options)
def get_proxy():
    url = "https://www.sslproxies.org/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html5lib")
    return {'https': (choice(list(map(lambda x:x[0]+':'+x[1],list(zip(map(lambda x:x.text,soup.findAll('td')[::8]),map(lambda x:x.text,soup.findAll('td')[1::8])))))))}

def proxy_request(request_type, url, **kwargs):
    while 1:
        try:
            proxy = get_proxy()
            # print("Using Proxy {}".format(proxy))
            r = requests.request(request_type, url, proxies=proxy, timeout=3, **kwargs)
            break
        except:
            pass
    return r
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url", ])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    driver = get_driver()
    urllib3.disable_warnings()
    
    base_url = "https://www.wawa.com"
    driver.get(base_url)
    cookies_list = driver.get_cookies()
        # print("cookies_list === " + str(cookies_list))
    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie['name']] = cookie['value']

    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(
    ",", ";")

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,gu;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': cookies_string,
        'Host': 'www.wawa.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.wawa.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    
    }
    r = proxy_request("get","https://www.wawa.com/site-map", verify=False, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup)
    for link in soup.find_all("ul",{"class":"CMSSiteMapList"})[-1].find_all("a",{"class":"CMSSiteMapLink"}):
        store_number = link['href'].split("/")[2]
        page_url = base_url + link['href']
        driver.get(page_url)
        cookies_list = driver.get_cookies()
        # print("cookies_list === " + str(cookies_list))
        cookies_json = {}
        for cookie in cookies_list:
            cookies_json[cookie['name']] = cookie['value']

        cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(
        ",", ";")  # use for header cookie
        r_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
            'Cookie': cookies_string,
        }
        #print(page_url)
        r1 = proxy_request("get",page_url, headers=r_headers, verify=False)
        soup1 = BeautifulSoup(r1.text, "lxml")
        location_name = soup1.find("span",{"itemprop":"name"}).text.strip()
        street_address = soup1.find("span",{"itemprop":"streetAddress"}).text.strip()
        city = soup1.find("span",{"itemprop":"addressLocality"}).text.strip()
        state = soup1.find("span",{"itemprop":"addressRegion"}).text.strip()
        zipp = soup1.find("span",{"itemprop":"postalCode"}).text.strip()
        phone = soup1.find("span",{"itemprop":"telephone"}).text.replace("Phone Number:","").strip()
        latitude = soup1.find("meta",{"itemprop":"latitude"})['content']
        longitude = soup1.find("meta",{"itemprop":"longitude"})['content']
        hours = soup1.find("meta",{"itemprop":"openinghours"})['content']

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        #print("data ==="+str(store))
        #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
        yield store


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
