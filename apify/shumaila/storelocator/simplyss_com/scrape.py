# Import libraries

from bs4 import BeautifulSoup
import csv
import string
import re
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('simplyss_com')


session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    url = 'https://www.simplyss.com'
    page = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(page.text, "html.parser")
    repo_list = soup.findAll('div',{'class': 'column'})
    cleanr = re.compile('<.*?>')
    phoner = re.compile('(.*?)')
    logger.info(len(repo_list))
    for repo in repo_list:
        link = repo.find('a')
        link = link['href']
        #logger.info('state=',link)
        page = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(page.text, "html.parser")
        maindiv = soup.find('div',{'id':'state-locations'})
        nextlist = maindiv.findAll('div',{'class':'location-display-new-box'})
        #logger.info("CITY COUNT =",len(nextlist))
        for nextlink in nextlist:
            store = nextlink['id'].split('-')[-1]
            link = nextlink.find('a')['href']
            logger.info('city=',link)
            page = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(page.text, "html.parser")
            soup = str(soup)
            start = soup.find("@context")
            start = soup.find("name", start)
            start = soup.find(":", start) + 3
            end = soup.find(",", start)
            title = soup[start:end - 1]
            #logger.info(title)
            start = soup.find("streetAddress")
            start = soup.find(":", start) + 3
            end = soup.find(",", start)
            street = soup[start:end - 1]
            #logger.info(street)
            start = soup.find("addressLocality")
            start = soup.find(":", start) + 3
            end = soup.find(",", start)
            city = soup[start:end - 1]
            #logger.info(city)
            start = soup.find("addressRegion")
            start = soup.find(":", start) + 3
            end = soup.find(",", start)
            state = soup[start:end - 1]
            #logger.info(state)
            start = soup.find("postalCode")
            start = soup.find(":", start) + 3
            end = soup.find(",", start)
            pcode = soup[start:end - 1]
            #logger.info(pcode)
            if len(pcode) < 4:
                pcode = "<MISSING>"
            start = soup.find("addressCountry")
            start = soup.find(":", start) + 3
            end = soup.find("}", start)
            ccode = soup[start:end - 1]
            ccode = re.sub("\r", "", ccode)
            ccode = re.sub("\n", "", ccode)
            ccode = re.sub('"', "", ccode)
            #logger.info(ccode)
            start = soup.find("latitude")
            start = soup.find(":", start) + 3
            end = soup.find(",", start)
            lat = soup[start:end - 1]
            #logger.info(lat)
            start = soup.find("longitude")
            start = soup.find(":", start) + 3
            end = soup.find("}", start)
            longt = soup[start:end - 2]
            longt = re.sub("\r", "", longt)
            longt = re.sub("\n", "", longt)
            longt = re.sub('"', "", longt)
            #logger.info(longt)
            start = soup.find("openingHours")
            start = soup.find(":", start) + 3
            end = soup.find('"', start+1)
            hours = soup[start:end]
            hours = hours.replace(",", "-")
            #logger.info(hours)
            start = soup.find("telephone")
            start = soup.find(":", start) + 3
            end = soup.find('"', start+1)
            phone = soup[start:end]
            phone = re.sub("\r", "", phone)
            phone = re.sub("\n", "", phone)
            phone = re.sub('"', "", phone)
            phone = phone.replace('+1 ','').lstrip()
            #logger.info(phone)
            #logger.info("....................................")
            ccode = ccode.rstrip()
            longt = longt.rstrip()
            if title.find('Coming Soon') == -1:
                data.append([
                        url,
                        link,
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
                        hours
                ])
                #logger.info(p,data[p])
                p += 1

    logger.info(p)
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
