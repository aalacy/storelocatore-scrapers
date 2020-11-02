# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import string
import re
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('chuys_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


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
    p = 0
    url = 'https://www.chuys.com/locations'
    r = session.get(url, headers=headers, verify=False)
    
    soup = BeautifulSoup(r.text, "html.parser")
    maindiv = soup.find('div', {'class': 'overview'})
    repo_list = maindiv.findAll('a')
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    for repo in repo_list:
        link = "https://www.chuys.com" + repo['href']
        #logger.info(link)
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        title = soup.find("title").text
        #logger.info(title)
        tempt = soup.find('h1').text
        maindiv = soup.find('div', {'class': 'location-info'})
        address = maindiv.find('p', {'class': 'address'}).text
        address = re.sub(pattern, "", address)
        #logger.info(address)
        address = str(address)
        start = address.find("|")
        street = address[0:start-1]
        street = street.replace(",", "")
        #logger.info(street)
        start = start + 2
        end = address.find(",", start)
        city = address[start:end-1]
        #logger.info(city)
        start = end + 2
        end = address.find(" ", start)
        state = address[start:end]
        #logger.info(state)
        start = end + 1
        end = len(address)
        pcode = address[start:end]
        #logger.info(pcode)
        phone = maindiv.find('p', {'class': 'phone'}).text
        phone = re.sub(pattern, "", phone)
        start = phone.find("|")
        if start != -1:
            phone = phone[2:start]
        else:
            phone = phone[2:len(phone)]
        #logger.info(phone)

        if len(phone) < 4:
            phone = "<MISSING>"
        hours = maindiv.find('p', {'class': 'hours'}).text
        hours = re.sub(pattern, " ", hours)
        if len(hours) < 4:
            hours = "<MISSING>"
        #logger.info(hours)
        if tempt.find('Coming Soon') == -1:
            data.append([
            url,
            link,
            title,
            street,
            city,
            state,
            pcode,
            "US",
            "<MISSING>",
            phone,
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
            hours
        ])
            logger.info(p,data[p])
            p += 1

    return data



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
