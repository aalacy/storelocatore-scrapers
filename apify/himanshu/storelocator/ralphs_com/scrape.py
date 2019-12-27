import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

requests.packages.urllib3.disable_warnings()

def requests_retry_session(
    retries=20,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504)
):
    session = requests.Session()
    proxy_password = os.environ["PROXY_PASSWORD"]
    proxy_url = "http://groups-RESIDENTIAL:{}@proxy.apify.com:8000/".format(proxy_password)
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    session.proxies = proxies
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = requests_retry_session()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    store_detail = []
    store_name = []
    return_main_object = []
    address1 = []
    location_name =[]    
    r = session.get("https://www.ralphs.com/storelocator-sitemap.xml", headers=headers)    
    soup = BeautifulSoup(r.text, "lxml")
    link1 = soup.find_all('loc')[:-1]
    for i in link1:
        link = i.text
        r1= session.get(link, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        main1=soup1.find('div', {'class': 'StoreAddress-storeAddressGuts'})
        if main1 != None:
            address_tmp1 =soup1.find('div', {'class': 'StoreAddress-storeAddressGuts'})
            address_tmp = list(address_tmp1.stripped_strings)
            address = address_tmp[0]
            city = address_tmp[1]
            state = address_tmp[3]
            zip = address_tmp[4]
            phone = soup1.find('span', {'class': 'PhoneNumber-phone'}).text
            hour = soup1.find('div', {'class': 'StoreInformation-storeHours'}).text
            location_name = soup1.find('h1', {'class': 'StoreDetails-header'}).text
        tem_var=[]           
        tem_var.append('https://www.ralphs.com/')
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append(zip)
        tem_var.append('US')
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hour)
        tem_var.append(link)
       
        if tem_var[2] in address1:
            continue
        address1.append(tem_var[2])
        return_main_object.append(tem_var) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
