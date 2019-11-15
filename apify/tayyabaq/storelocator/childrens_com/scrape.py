import csv
import os
import re, time
import requests
from lxml import html
from bs4 import BeautifulSoup
import json
import lxml.html
import urllib.request as urllib2

def write_output(data):
    with open('data.csv', mode='wb') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def fetch_data():
    data=[];hours_of_operation=[]; latitude=[];longitude=[];zipcode=[];location_name=[];city=[];street_address=[]; state=[]; phone=[]
    url = "https://www.childrens.com/wps/FusionServiceCMC/publicsearch/api/apollo/collections/Childrens/query-profiles/ls/select?q=*&start=0&rows=100"
    content = json.load(urllib2.urlopen(url))
    title=re.findall(r"title_s(.*?)\}", str(content))
    location_name = [title[n].split("u'")[-1].replace("'","").replace(': u"','').replace('"','') for n in range(1,len(title))]
    address=re.findall(r'streetAddress_ss(.*?)\]', str(content))
    street_address = [address[n].replace("': [u'","").replace(", u'"," ").replace("'","") for n in range(1,len(address))]
    phones=re.findall(r'telephone_s(.*?)\,', str(content))
    zipc=re.findall(r'postalCode_s(.*?)\,', str(content))
    zipcode = [zipc[n].replace("': u'","").replace("'","") for n in range(1,len(zipc))]
    states=re.findall(r'addressRegion_s(.*?)\,', str(content))
    state = [states[n].replace("': u'","").replace("'","") for n in range(1,len(states))]
    cities=re.findall(r'addressLocality_s(.*?)\,', str(content))
    city = [cities[n].replace("': u'","").replace("'","") for n in range(1,len(cities))]
    lat_lon = re.findall(r'latlng_p(.*?)\',', str(content))
    latitude = [lat_lon[n].replace("': u'","").split(",")[0] for n in range(1,len(lat_lon))]
    longitude = [lat_lon[n].replace("': u'","").split(",")[1] for n in range(1,len(lat_lon))]
    page = re.findall(r"id':(.*?)\,", str(content))
    page_url = [page[n].replace(" u'","").replace("'","").strip() for n in range(0,len(page))]
    analyze = re.findall(r'title_s(.*?)\postalCode_s', str(content))
    for n in range(0,len(analyze)):
        try:
            phone.append(analyze[n].split("telephone_s': u'")[1].split("',")[0])
        except:
            if (n==0) and (location_name[0]=="Children\u2019s Health\u2120 Andrews Institute for Orthopaedics & Sports Medicine"):
                phone.append("469-303-3000")
            else:
                phone.append("<MISSING>")
    for n in range(0,len(location_name)): 
        data.append([
            'https://www.childrens.com/',
            page_url[n],
            location_name[n],
            street_address[n],
            '<MISSING>',
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            '<INACCESSIBLE>'
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
