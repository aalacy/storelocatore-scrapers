import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import time
from random import choice
import html5lib
import pprint
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import http.client
import platform
session = SgRequests()
system = platform.system()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
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
    r = session.get(url)
    soup = BeautifulSoup(r.content, "html5lib")
    return {'https': (choice(list(map(lambda x:x[0]+':'+x[1],list(zip(map(lambda x:x.text,soup.findAll('td')[::8]),map(lambda x:x.text,soup.findAll('td')[1::8])))))))}
def proxy_request(request_type, url, **kwargs):
    while 1:
        try:
            proxy = get_proxy()
            #print("Using Proxy {}".format(proxy))
            r = requests.request(request_type, url, proxies=proxy, timeout=5, **kwargs)
            break
        except:
            pass
    return r
def fetch_data():    
    headers ={
        'authority': 'www.crateandbarrel.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.crateandbarrel.com',
        'referer': 'https://www.crateandbarrel.com/stores/list-state/retail-stores',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',     
    }
    base_url = "https://www.crateandbarrel.com/"
    r = proxy_request('POST', "https://www.crateandbarrel.com/stores/locator", headers=headers, data="SearchKeyword=85251&hdnHostUrl=https%3A%2F%2Fwww.crateandbarrel.com")
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup)
    data = soup.find(lambda tag: (tag.name == "script") and '"StoreList":' in tag.text).text
    #print(data)
    json_data = json.loads(data.split('Crate.Model,')[1].split(');$')[0])
    for i in json_data['AllStoreList']:
        location_name = i['Name']
        store_number = i['StoreNumber']
        street_address = i['Address1']+" "+i['Address2']
        city = i['City']
        state = i['State']
        zipp = i['Zip']
        # print(zipp)
        if "Philippines" in i['Country']:
            continue
        country_code = i['Country'].replace("USA","US").replace("CAN","CA")
        phone = "("+i['PhoneAreacode']+")"+" "+i['PhonePrefix']+"-"+i['PhoneSuffix']
        location_type = "Store"
        latitude = i['StoreLat']
        longitude = i['StoreLong']
        page_url = "https://www.crateandbarrel.com/stores/"+str(location_name.lower().replace(',','').replace(' ','-'))+"/str"+str(store_number)
        # print(page_url)
        driver = get_driver()
        driver.get(page_url)
        cookies_list = driver.get_cookies()
        # print("cookies_list === " + str(cookies_list))
        # exit()
        cookies_json = {}
        for cookie in cookies_list:
            cookies_json[cookie['name']] = cookie['value']
        cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(",", ";")  # use for header cookie
        r_headers = {       
            'authority': 'www.crateandbarrel.com',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'cookie': cookies_string,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
        }
        driver.quit()
        r1 = proxy_request('get', page_url, headers=r_headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        if soup1.find("ul",{"class":"hours"}):
            hours = ' '.join(list(soup1.find("ul",{"class":"hours"}).stripped_strings))
            # print(hours)
        else:
            hours = "<INACCESSIBLE>"
            # print(hours)     
        store = []
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours if hours else "<MISSING>")
        store.append(page_url.replace("-/","/").replace("---","-") if page_url else "<MISSING>")
      #  print("data =="+str(store))
      #  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
