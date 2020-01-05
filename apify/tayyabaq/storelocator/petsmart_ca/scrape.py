import csv
import os
import requests
from bs4 import BeautifulSoup
import re, time
import datetime

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    data = []
    store_links =[]
    clear_links =[]
    #CA stores
    url = 'https://www.petsmart.ca/store-locator/all/'
    u='https://www.petsmart.ca/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    store=soup.find('div',class_='all-states-list container')
    str=store.find_all("a")
    for i in str:
        newurl=i['href']
        page = requests.get(newurl)
        soup = BeautifulSoup(page.content, "html.parser")
        store=soup.find_all('a', class_='store-details-link')
        for j in store:
            ul=u+j['href']
            page = requests.get(ul)
            soup = BeautifulSoup(page.content, "html.parser")
            loc=soup.find('h1', class_ ='store-name').text
            street = soup.find('div', itemprop='streetAddress').text
            city = soup.find('span',itemprop='addressLocality')
            cty=city.text
            sts = city.find_next('span',itemprop='addressLocality').text
            zcode = soup.find('span',itemprop='postalCode').text
            num=j['id']
            ph=soup.find("a",class_="store-contact-info").text
            lat=soup.find("meta",itemprop='latitude')['content']
            lng=soup.find("meta",itemprop='longitude')['content']
            hr=soup.find_all("span",itemprop="dayOfWeek")  
            op=soup.find_all("time",itemprop='opens')
            cl=soup.find_all("time",itemprop='closes')
            hours=""
            for k in range(0,len(op)) :
                hours+=hr[k].text+" "
                hours+=op[k]['content']+"-"
                hours+=cl[k]['content']+" "
            now = datetime.datetime.now()
            dy=now.strftime("%a").upper()
            hours=hours.replace("TODAY",dy)
            data.append([
                'https://www.petmarts.ca/',
                 ul,
                loc,
                street,
                cty,
                sts,
                zcode,
                'CA',
                num,
                ph,
                '<MISSING>',
                lat,
                lng,
                hours
                ])
         
    return data
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()