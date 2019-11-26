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
    p = 1
    url = 'https://locations.rentacenter.com/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    mainul = soup.find('ul',{'class':'list-group'})
    statelinks = mainul.findAll('a')
    for states in statelinks:
        statelink = "https://locations.rentacenter.com" + states['href']
       # print(statelink)
        page1 = requests.get(statelink)
        soup1 = BeautifulSoup(page1.text, "html.parser")
        mainul1 = soup1.find('ul', {'class': 'list-group'})
        citylinks = mainul1.findAll('a')
        for cities in citylinks:
            citylink =  "https://locations.rentacenter.com" + cities['href']
            #print(citylink)
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

            else:
                data.append(extract(soup2,citylink))
    return data

def extract(soup,link):
    try:
        hourd = soup.find('dl', {'class': 'list-hours'}).text
        hourd = hourd.replace("\n", " ")
        hourd = hourd.strip()
    except:
        hourd = "<MISSING>"
    script = soup.find("script",{'type':'application/ld+json'})
    script = str(script)
    start = script.find('"addressCountry"')
    start = script.find(":", start) + 1
    end = script.find(",", start)
    ccode = script[start:end]
    ccode = ccode.replace('"',"")
    start = script.find('"addressLocality"')
    start = script.find(":", start) + 1
    end = script.find(",", start)
    city = script[start:end]
    city = city.replace('"', "")
    start = script.find('"addressRegion"')
    start = script.find(":", start) + 1
    end = script.find(",", start)
    state = script[start:end]
    state = state.replace('"', "")
    start = script.find('"postalCode"')
    start = script.find(":", start) + 1
    end = script.find(",", start)
    pcode = script[start:end]
    pcode = pcode.replace('"', "")
    start = script.find('"streetAddress"')
    start = script.find(":", start) + 1
    end = script.find("}", start)
    street = script[start:end]
    street = street.replace('"', "")
    start = script.find('"branchCode"')
    start = script.find(":", start) + 1
    end = script.find(",", start)
    store = script[start:end]
    store= store.replace('"', "")
    start = script.find('"latitude"')
    start = script.find(":", start) + 1
    end = script.find(",", start)
    lat = script[start:end]
    lat = lat.replace('"', "")
    start = script.find('"longitude"')
    start = script.find(":", start) + 1
    end = script.find("}", start)
    longt= script[start:end]
    longt = longt.replace('"', "")
    start = script.find('"telephone"')
    if start != -1:
        start = script.find(":", start) + 1
        end = script.find(",", start)
        phone = script[start:end]
        phone = phone.replace('"', "")
    else:
        phone = "<MISSING>"
    title = soup.find('title').text
    start = title.find(",")
    if start != -1:
        title = title[0:start]
    start = title.find("|")
    if start != -1:
        title = title[0:start]

    data = ['https://www.rentacenter.com/', link, title, street, city, state, pcode, ccode, store, phone, '<MISSING>', lat,longt, hourd]
    #print(data)
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()

