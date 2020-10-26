# Import libraries

import requests
from bs4 import BeautifulSoup
import csv
import string
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('wyndhamhotels_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    url = 'https://www.wyndhamhotels.com/wingate/locations'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    repo_list = soup.findAll('li',{'class': 'property'})
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s+')
    for repo in repo_list:
        link = repo.find('a')
        link = "https://www.wyndhamhotels.com"+ link['href']
        logger.info(link)
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        ddiv = soup.find('div', {'class': 'property-info'})
        #logger.info(ddiv)
        soup = str(soup)
        start = soup.find('overview_propertyId')
        start = soup.find("=",start) + 3
        end = soup.find(";", start)
        store = soup[start:end-1]
        logger.info(store)
        start = soup.find('property_country_code')
        start = soup.find("=", start) + 3
        end = soup.find(";", start)
        ccode = soup[start:end - 1]
        logger.info(ccode)
        start = soup.find("@context")
        start = soup.find("name",start)
        start = soup.find(":", start) + 2
        end = soup.find(",", start)
        title = soup[start:end - 1]
        logger.info(title)
        start = soup.find("streetAddress")
        start = soup.find(":",start)+2
        end = soup.find(",", start)
        street = soup[start:end - 1]
        logger.info(street)
        start = soup.find("addressLocality")
        start = soup.find(":", start) + 2
        end = soup.find(",", start)
        city = soup[start:end - 1]
        logger.info(city)
        start = soup.find("addressRegion")
        start = soup.find(":", start) + 2
        end = soup.find(",", start)
        state = soup[start:end - 1]
        logger.info(state)
        start = soup.find("postalCode")
        start = soup.find(":", start) + 2
        end = soup.find(",", start)
        pcode = soup[start:end - 1]
        logger.info(pcode)
        start = soup.find("latitude")
        start = soup.find(":", start) + 1
        end = soup.find(",", start)
        lat = soup[start:end - 1]
        logger.info(lat)
        start = soup.find("longitude")
        start = soup.find(":", start) +1
        end = soup.find("}", start)
        longt = soup[start:end - 1]
        longt = re.sub("\r","",longt)
        longt = re.sub("\n", "", longt)
        logger.info(longt)
        start = soup.find("telephone")
        start = soup.find(":", start) + 2
        end = soup.find(",", start)
        phone = soup[start:end - 1]
        if len(phone) > 16:
            phone = "<MISSING>"
        logger.info(phone)

        if ccode == "US" or ccode == "CA":
            data.append([
                url,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                "<MISSING>"
            ])

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
