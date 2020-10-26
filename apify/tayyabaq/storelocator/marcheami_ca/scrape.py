import csv
import os
import re, time
import requests
import itertools
from bs4 import BeautifulSoup
import json
import lxml.html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #return webdriver.Chrome('c:/chromedriver.exe', chrome_options=options)
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    driver = get_driver()
    data=[];page_url=[];hours_of_operation=[]; latitude=[];longitude=[];zipcode=[];location_name=[];city=[];street_address=[]; state=[]; phone=[]
    url = "http://marcheami.ca/siteamienglish/index.php"
    r = requests.get(url)
    c=0
    soup = BeautifulSoup(r.content, 'html.parser')
    doc = lxml.html.fromstring(r.content)
    store = doc.xpath('//ul[@class="rvnavigator"]/li[5]/ul/li/a/@href')
    states = doc.xpath('//ul[@class="rvnavigator"]/li[5]/ul/li/a/span/text()')
    for n in range(0,len(store)):
        driver.get(store[n])
        time.sleep(4)
        name = driver.find_elements_by_xpath('//div[@class="store"]/h2')
        address =  driver.find_elements_by_xpath('//div[@class="store"]/ul/li[1]')
        cities =  driver.find_elements_by_xpath('//div[@class="store"]/ul/li[2]')
        phones =  driver.find_elements_by_xpath('//div[@class="store"]/ul/li[3]')
        name1 = driver.find_elements_by_xpath('//div[@class="store last"]/h2')
        address1 =  driver.find_elements_by_xpath('//div[@class="store last"]/ul/li[1]')
        cities1 =  driver.find_elements_by_xpath('//div[@class="store last"]/ul/li[2]')
        phones1 =  driver.find_elements_by_xpath('//div[@class="store last"]/ul/li[3]')
        name2 = driver.find_elements_by_xpath('//div[@class="store alone"]/h2')
        address2 =  driver.find_elements_by_xpath('//div[@class="store alone"]/ul/li[1]')
        cities2 =  driver.find_elements_by_xpath('//div[@class="store alone"]/ul/li[2]')
        phones2 =  driver.find_elements_by_xpath('//div[@class="store alone"]/ul/li[3]')
        for m in range(0,len(address)):
            if "1040 C, ROUTE 195" == address[m].text:
                print("here")
                c+=1
                if c>1:
                    continue
            
            location_name.append(name[m].text)
            street_address.append(address[m].text)
            if states[n] in ['Bas St-Laurent','Chaudières Appalaches','Centre du Québec','Outaouais','Saguenay','Côte Nord','Estrie','Gaspésie','Lanaudière','Laurentides','Mauricie','Montérégie','Montréal']:
                state.append("Quebec")
            elif states[n] in ['Clair / New-Brunswick']:
                state.append("New Brunswick")
            else:
                state.append(states[n])
            city.append(cities[m].text)
            phone.append(phones[m].text)
            page_url.append(store[n])
        for x in range(0,len(address1)):
            location_name.append(name1[x].text)
            street_address.append(address1[x].text)
            if states[n] in ['Bas St-Laurent','Chaudières Appalaches','Centre du Québec','Saguenay','Outaouais','Côte Nord','Estrie','Gaspésie','Lanaudière','Laurentides','Mauricie','Montérégie','Montréal']:
                state.append("Quebec")
            elif states[n] in ['Clair / New-Brunswick']:
                state.append("New Brunswick")
            else:
                state.append(states[n])
            city.append(cities1[x].text)
            phone.append(phones1[x].text)
            page_url.append(store[n])
        for y in range(0,len(address2)):
            location_name.append(name2[y].text)
            street_address.append(address2[y].text)
            if states[n] in ['Bas St-Laurent','Chaudières Appalaches','Centre du Québec','Saguenay','Outaouais','Côte Nord','Estrie','Gaspésie','Lanaudière','Laurentides','Mauricie','Montérégie','Montréal']:
                state.append("Quebec")
            elif states[n] in ['Clair / New-Brunswick']:
                state.append("New Brunswick")
            else:
                state.append(states[n])
            city.append(cities2[y].text)
            phone.append(phones2[y].text)
            page_url.append(store[n])
        
    for n in range(0,len(location_name)): 
        print(page_url[n])
        data.append([
            'https://marcheami.ca/',
            page_url[n],
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            '<MISSING>',
            'CA',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            '<MISSING>'
        ])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()