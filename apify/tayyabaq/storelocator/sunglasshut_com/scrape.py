# -*- coding: utf-8 -*-
import csv
import os
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re, time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
def fetch_data():
    data = []
    store_links =[]
    clear_links =[]
    #CA stores
    urls = ['https://stores.sunglasshut.com/ca.html','https://stores.sunglasshut.com/gb.html','https://stores.sunglasshut.com/us.html']
    u='https://stores.sunglasshut.com/'
    for url in urls:
        page = session.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        store=soup.find_all('a',class_='c-directory-list-content-item-link')
        for i in store:
            newurl=u+i['href']
            page = session.get(newurl)
            soup = BeautifulSoup(page.content, "html.parser")
            store=soup.find_all('a',class_='c-directory-list-content-item-link')
            if len(store)==0:
                lnk=soup.find_all('h5',class_='c-location-grid-item-title')
                if len(lnk) == 0:
                    store_links.append(newurl)
                else:
                    for m in lnk:
                        h=m.find("a")['href']
                        ul=u+h
                        ul=ul.replace("../","")
                        store_links.append(ul)
            else:
                for j in store:
                    nurl=u+j['href']
                    nurl=nurl.replace("../","")
                    page = session.get(nurl)
                    soup = BeautifulSoup(page.content, "html.parser")
                    loc=soup.find('div',class_='banner-h1-content h1-large').text
                    if 'Locationsin ' in loc:
                        lnk=soup.find_all('h5',class_='c-location-grid-item-title')
                        for m in lnk:
                            h=m.find("a")['href']
                            ul=u+h
                            ul=ul.replace("../","")
                            store_links.append(ul)
                    else:
                        store_links.append(nurl)
    for u in store_links:
        page = session.get(u)
        soup = BeautifulSoup(page.content, "html.parser")
        loc=soup.find('div',class_='banner-h1-content h1-large').text
        if loc == "":
            loc='<MISSING>'
        lat=soup.find('meta',itemprop='latitude')['content']
        lng=soup.find('meta',itemprop='longitude')['content']
        try :
            ctry=soup.find('span',itemprop='addressCountry').text
        except:
            ctry = '<MISSING>'                    
        strt=soup.find_all('span',itemprop='streetAddress')
        street=""
        for k in strt:
            street+=k.text
            street+=" "
        if len(strt)== 0:
            street='<MISSING>'
        try:
            cty=soup.find('span',itemprop='addressLocality').text
        except:
            cty = '<MISSING>'  
        cty=cty.replace(",","")
        try:
            sts=soup.find('span',itemprop='addressRegion').text
        except:
            sts ='<MISSING>'  
        try:
            zcode=soup.find('span',itemprop='postalCode').text
        except:
            zcode = '<MISSING>'  
        try :
            ph=soup.find('span',itemprop='telephone').text
        except:
            ph = '<MISSING>'  
        hr=soup.find_all('meta',itemprop='openingHours')
        hours =""
        for l in hr:
            hours+=l['content']
            hours+=" "
        if hours == "":
            hours='<MISSING>'
        hours=hours.replace("Mo","MON")
        hours=hours.replace("Tu","TUE")
        hours=hours.replace("We","WED")
        hours=hours.replace("Th","THU")
        hours=hours.replace("Fr","FRI")
        hours=hours.replace("Sa","SAT")
        hours=hours.replace("Su","SUN")
        data.append([
             'https://www.sunglasshut.com/',
              u.replace(u'\u2019',''),
             loc.replace(u'\u2019',''),
             street.replace(u'\u2019',''),
             cty.replace(u'\u2019',''),
             sts.replace(u'\u2019',''),
             zcode.replace(u'\u2019','').replace("\r\n","").replace("\n","").strip(),
             ctry.replace(u'\u2019',''),
             '<MISSING>',
             ph.replace(u'\u2019',''),
             '<MISSING>',
             lat.replace(u'\u2019',''),
             lng.replace(u'\u2019',''),
             hours.replace(u'\u2019','')
             ])
    return data
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
