# https://orthodontist.smiledoctors.com/
# https://www.getngo.com/locations/

import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('orthodontist_smiledoctors_com')




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
    url = 'https://orthodontist.smiledoctors.com/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    link_list = soup.findAll('a',{'class':'link'})
    for alink in link_list:
        alink = alink['href']
        logger.info(alink)
        if alink.find('https') > -1:
            page = requests.get(alink)
            soup = BeautifulSoup(page.text, "html.parser")
            maindiv = soup.findAll('div', {'class': 'col1'})
            for div in maindiv:
                link = div.find('a')
                link = link['href']
                logger.info(link)
                page1 = requests.get(link)
                soup1 = BeautifulSoup(page1.text, "html.parser")
                hdetail = soup1.find('div', {'class': 'banner'})
                title = hdetail.find('h1').text
                hdetail = hdetail.findAll('p')
                address = hdetail[0].text
                start = address.find(",",0)
                street = address[0:start]
                start = start + 3
                end =  address.find(",",start)
                city = address[start:end]
                start = end + 2
                end = address.find(" ", start)
                state = address[start:end]
                start =  end + 1
                end = len(address)
                pcode = address[start:end]

                try:
                    phone = hdetail[1].find('a').text
                except:
                    phone = "<MISSING>"

                hdetail = soup1.find('div', {'class': 'section one align-left'})
                hours = hdetail.find('p').text

                hdetail = soup1.find('div', {'class': 'bottom-section'})
                hdetail = hdetail.find('a')
                hdetail = hdetail['href']
                start = hdetail.find('@') + 1
                end = hdetail.find(',', start)
                lat = hdetail[start:end]
                start = end + 1
                end = hdetail.find(',', start)
                longt = hdetail[start:end]
                if hours.find("Clinic hours can vary") > -1:
                    hours = "<MISSING>"
                #logger.info(title)
                #logger.info(street)
                #logger.info(city)
                #logger.info(state)
                #logger.info(pcode)
                #logger.info(phone)
                logger.info(hours)
                #logger.info(lat)
                #logger.info(longt)
                if street.find('Grand Opening') == -1:
                    data.append([
                        'https://orthodontist.smiledoctors.com/',
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        "<MISSING>",
                        phone,
                        "<MISSING>",
                        lat,
                        longt,
                        hours
                    ])

            #logger.info(("..................."))

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

