import requests
from bs4 import BeautifulSoup
import csv
import string
import re
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('searsoptical_com')




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
    url = 'https://locations.searsoptical.com/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    statelinks = soup.findAll('a',{'class':'c-directory-list-content-item-link'})
    #logger.info(len(statelinks))
    for states in statelinks:
        statelink = "https://locations.searsoptical.com/" + states['href']
        #logger.info("state = ", statelink)
        page1 = requests.get(statelink)
        soup1 = BeautifulSoup(page1.text, "html.parser")
        citylinks = soup1.findAll('a', {'class': 'c-directory-list-content-item-link'})
        #logger.info("cities = ",len(citylinks))
        if len(citylinks) > 0:
            for cities in citylinks:
                citylink = "https://locations.searsoptical.com/" + cities['href']
                #logger.info("city = ",citylink)
                page2 = requests.get(citylink)
                soup2 = BeautifulSoup(page2.text, "html.parser")
                try:
                    data.append(extract(soup2,citylink))
                except:
                    branchlinks = soup2.findAll('div', {'class': 'c-location-grid-item-link-wrapper'})
                    for branch in branchlinks:
                        branch = branch.find('a')
                        branchlink = "https://locations.searsoptical.com/" + branch['href']
                        branchlink = branchlink.replace("../","")
                        #logger.info("branch = ", branchlink)
                        page3 = requests.get(branchlink)
                        soup3 = BeautifulSoup(page3.text, "html.parser")
                        data.append(extract(soup3,branchlink))

        else:
            try:
                data.append(extract(soup1,statelink))

            except:
                branchlinks =soup1.findAll('div',{'class':'c-location-grid-item-link-wrapper'})
                for branch in branchlinks:
                    branch = branch.find('a')
                    branchlink = "https://locations.searsoptical.com/" + branch['href']
                    branchlink = branchlink.replace("../", "")
                    #logger.info("branch = ", branchlink)
                    page3 = requests.get(branchlink)
                    soup3 = BeautifulSoup(page3.text, "html.parser")
                    data.append(extract(soup3,branchlink))


    return data

def extract(soup,link):
    title = soup.find('h1',{'id':'location-name'}).text
    lat = soup.find('meta',{'itemprop':'latitude'})
    lat = lat['content']
    longt = soup.find('meta', {'itemprop': 'longitude'})
    longt = longt['content']
    street = soup.find('span', {'itemprop': 'streetAddress'}).text
    ccode = soup.find('span', {'itemprop': 'addressCountry'}).text
    city = soup.find('span', {'itemprop': 'addressLocality'}).text
    state = soup.find('span', {'itemprop': 'addressRegion'}).text
    pcode = soup.find('span', {'itemprop': 'postalCode'}).text
    try:
        phone = soup.find('span', {'itemprop': 'telephone'}).text
    except:
        phone = "<MISSING>"
    try:
        hourd = soup.find('table', {'class': 'c-location-hours-details'})
        hourd = hourd.findAll('tr')
        hours = ""
        for hour in hourd:
            hours = hours + hour.text +" "
        hours = hours.replace("day","day ")
    except:
        hours = "<MISSING>"
    soup  = str(soup)
    start = soup.find("storeNumber")
    start = soup.find("=", start) + 1
    end = soup.find("&", start)
    store = soup[start:end]
    pcode = pcode.strip()
    if len(store) > 9:
        store = "<MISSING>"
    #logger.info(link)
    #logger.info(title)
    #logger.info(store)
    #logger.info(street)
    #logger.info(city)
    #logger.info(state)
    #logger.info(pcode)
    #logger.info(ccode)
    #logger.info(phone)
    #logger.info(hours)
    #logger.info(lat)
    #logger.info(longt)
    data = ['https://searsoptical.com/',link,title,street,city,state,pcode,ccode,store,phone,'<MISSING>',lat,longt,hours]
    #logger.info(data)
    return data

def scrape():
    data = fetch_data()

    write_output(data)


scrape()
