import requests
from bs4 import BeautifulSoup
import csv
import string
import re
import usaddress


def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    p = 0
    url = 'https://locations.rentacenter.com/#contains-place-toggle'
    
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    mainul = soup.find('div',{'id':'contains-place'})
    statelinks = mainul.findAll('a')
    #print(statelinks)
    for states in statelinks:
        statelink = 'https://locations.rentacenter.com'+ states['href']+'#contains-place-toggle'
        print(statelink)
        page1 = requests.get(statelink)
        soup1 = BeautifulSoup(page1.text, "html.parser")
        mainul1 = soup1.find('div', {'id': 'contains-place'})
        citylinks = mainul1.findAll('a')
        for cities in citylinks:
            citylink = 'https://locations.rentacenter.com'+ cities['href']
            print(citylink)
            page2 = requests.get(citylink)
            soup2 = BeautifulSoup(page2.text, "html.parser")
            mainul2 = soup2.find('ul', {'class': 'list-group'})
            branchlinks = mainul2.findAll('a',{'itemprop':'address'})
            if len(branchlinks) > 0:
                for branch in branchlinks:
                    branchlink = "https://locations.rentacenter.com" + branch['href']
                    #print(branchlink)
                    page3 = requests.get(branchlink)
                    soup3 = BeautifulSoup(page3.text, "html.parser")
                    data.append(extract(soup3,branchlink))
                    print(p,data[p])
                    p += 1

            else:
                data.append(extract(soup2,citylink))
                #print(p,data[p])
                p += 1
            
            
    return data

def extract(soup,link):
    try:
        hourd = soup.find('div', {'class': 'hours'}).find('dd').text
        hourd = hourd.replace("\n", " ")
        hourd = hourd.strip()
    except:
        hourd = "<MISSING>"
    
    title = soup.find('title').text
    start = title.find(",")
    if start != -1:
        title = title[0:start]
    start = title.find("|")
    if start != -1:
        title = title[0:start]

    try:
        street = soup.find('div',{'class':'street'}).text.replace('\n','').lstrip().rstrip()
    except:
        street = '<MISSING>'
    try:
        det = soup.find('div',{'class':'locality'}).text.replace('\n',' ').lstrip()
        
        city ,state= det.split(', ')
        
        state, pcode = state.lstrip().split(' ',1)
        pcode = pcode.lstrip().rstrip()
        state  = state.lstrip().rstrip()
       
       
    except:
        state= '<MISSING>'
        city='<MISSING>'
        pcode ='<MISSING>'
        
    try:
        phone = soup.find('a',{'class':'list-location-phone-number'}).text
    except:
        phone = '<MISSING>'

    try:
        coord = soup.find('a',{'class':'list-location-secondary-anchor'})['href']
        start = coord.find('+')
        start = coord.find('/',start)+1
        end = coord.find(',',start)
        lat = coord[start:end]
        start = end +1
        end = len(coord)
        longt = coord[start:end]
    except:
        lat = '<MISSING>'
        longt = '<MISSING>'
    try:    
        store = soup.find('div',{'id':'location-list'})['data-currentlocation']
        print(store)
    except:
        store ='<MISSING>'
        

    data = ['https://www.rentacenter.com/', link, title, street, city, state, pcode,'US', store, phone, '<MISSING>', lat ,longt, hourd]
    #print(data)
    #input()
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()

