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
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data=[];location_name=[];page_url=[];street_address=[];city=[];state=[];zipcode=[];phone=[];latitude=[];longitude=[];typ=[];hrs=[];
    url = "https://www.childrens.com/wps/FusionServiceCMC/publicsearch/api/apollo/collections/Childrens/query-profiles/ls/select?q=*&start=0&rows=100"
    content = json.load(urllib2.urlopen(url))
    res=content['response']
    docs=res['docs']
    print(len(docs))
    for i in range(0,len(docs)):
        loc=docs[i]
        l=str(loc)
        pg=(l.split("\'id\': \'"))[1].split("\'")[0]
        coord=loc['latlng_p']
        lat=coord.split(",")[0]
        long=coord.split(",")[1]
        page_url.append(pg)
        latitude.append(lat)
        longitude.append(long)
        
    print(len(page_url))   
    for link in page_url:
        print(link)
        page = requests.get(link)
        soup = BeautifulSoup(page.content,"html.parser")
        loc=soup.find("h1",itemprop='name').text
        loc=loc.replace("\u2120","")
        loc=loc.replace("\n","")
        try:
            hr=soup.find("span",itemprop="openingHours").text
        except:
            hrs.append(hr)
        else:
            hrs.append("<MISSING>")
        street=soup.find("span",itemprop="streetAddress").text
        street=street.replace("\n","")
        cty=soup.find("span",itemprop='addressLocality').text
        cty=cty.replace(",","")
        ste=soup.find("span",itemprop='addressRegion').text
        zcode=soup.find("span",itemprop='postalCode').text
        ph=soup.find("span",itemprop='telephone').text
        location_name.append(loc)
        street_address.append(street)
        city.append(cty)
        state.append(ste)
        zipcode.append(zcode)
        hrs.append(hr)
        if any(c.isalpha() for c in ph):
            phone.append("<MISSING>")
        elif ph == "":
            phone.append("<MISSING>")
        else:
            phone.append(ph)
        
    c=0    
    for n in range(0,len(location_name)): 
        cnt = False
        for i in data:
            if location_name[n] == i[2]:
                cnt= True
        if cnt == False:
            data.append([
                'https://www.childrens.com/',
                 page_url[n],
                 location_name[n],
                 street_address[n],
                 city[n],
                 state[n],
                 zipcode[n],
                 'US',
                 '<MISSING>',
                 phone[n],
                 '<MISSING>',
                 latitude[n],
                 longitude[n],
                 hrs[n]
                 ])
    print(len(data))
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()