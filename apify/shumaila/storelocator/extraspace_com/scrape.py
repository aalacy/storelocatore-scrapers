# https://orthodontist.smiledoctors.com/
# https://www.getngo.com/locations/

import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here

    data = []
    pattern = re.compile(r'\s\s+')
    url = 'https://www.extraspace.com/storage/facilities/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    state_list = soup.findAll('a',{'class':'state-link'})
    p = 1
    for alink in state_list:
        links = []
        statelink = "https://www.extraspace.com" + alink['href']
        #print(statelink)
        page1 = requests.get(statelink)
        soup1 = BeautifulSoup(page1.text, "html.parser")
        #link_list = soup1.findAll('a', {'class': 'address-link'})
       # for alink in link_list:s
        #    links.append("https://www.extraspace.com" + alink['href'])
        link_list = soup1.findAll('a', {'class': 'cl-other-faclink'})
        for alink in link_list:
            links.append("https://www.extraspace.com" + alink['href'])
        print(len(links))
        for alink in links:
            try:
                link = alink #"https://www.extraspace.com" + alink['href']
                #print(link)
                page2 = requests.get(link)
                soup2 = BeautifulSoup(page2.text, "html.parser")
                title = soup2.find('span',{'id': 'FacilityTitle'}).text
                street = soup2.find('span', {'id': 'ctl00_mContent_lbAddress'}).text
                city = soup2.find('span', {'id': 'ctl00_mContent_lbCity'}).text
                state = soup2.find('span', {'id': 'ctl00_mContent_lbState'}).text
                pcode = soup2.find('span', {'id': 'ctl00_mContent_lbPostalCode'}).text
                phone =soup2.find('span', {'class': 'tel'}).text
                detail = soup2.findAll('div',{'class': 'fac-info'})
                hdet = detail[2].text
                hdet = re.sub(pattern," ",hdet)
                hdet = hdet.replace("\n", " ")
                start = hdet.find("Storage Gate Hours")
                hours = hdet[start:len(hdet)]
                soup2 = str(soup2)
                start = soup2.find('storeCSID')
                start = soup2.find(':', start) + 3
                end = soup2.find("'", start)
                store = soup2[start:end]
                start = soup2.find('latitude')
                start = soup2.find(':', start) + 3
                end = soup2.find('"', start)
                lat = soup2[start:end]
                start = soup2.find('longitude')
                start = soup2.find(':', start) + 3
                end = soup2.find('"', start)
                longt = soup2[start:end]
                #print(len(hdet))
                #print(link)
                #print(title)
                #print(store)
                #print(street)
                #print(city)
                #print(state)
                #print(pcode)
                #print(phone)
                #print(hours)
                #print(lat)
                #print(longt)
                print(p)

                p += 1
                title = title.replace("?","")
                flag = True
                #print(len(data))


                if flag:
                    data.append([
                        'https://www.extraspace.com',
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone,
                        "<MISSING>",
                        lat,
                        longt,
                        hours
                    ])
            except:
                pass
        print(".................")

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

