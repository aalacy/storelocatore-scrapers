import requests
from bs4 import BeautifulSoup
import csv
import string
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lewisdrug_com')




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
    p = 1
    url = 'https://www.lewisdrug.com/stores'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    repo_list = soup.findAll('div', {'class': 'store-content'})
    cleanr = re.compile('<.*?>')

    p = 0
    for repo in repo_list:
        links = repo.findAll('a')
        for link in links:
           if link.text == "Details ":
                link = link['href']
                #logger.info(link)
                #logger.info(p)
                page = requests.get(link)
                soup = BeautifulSoup(page.text, "html.parser")
                scriptlist = soup.findAll('script', {'type': 'application/ld+json'})
                detail = str(scriptlist[3])
                #logger.info(detail)
                start = detail.find("name", 0)
                start = detail.find(":", start) + 3
                end = detail.find(",", start) - 1
                title = detail[start:end]

                start = detail.find("streetAddress", end)
                start = detail.find(":", start) + 3
                end = detail.find(",", start) - 1
                street = detail[start:end]

                start = detail.find("addressLocality", end)
                start = detail.find(":", start) + 3
                end = detail.find(",", start) - 1
                city = detail[start:end]

                start = detail.find("addressRegion", end)
                start = detail.find(":", start) + 3
                end = detail.find(",", start) - 1
                state = detail[start:end]

                start = detail.find("postalCode", end)
                start = detail.find(":", start) + 3
                end = detail.find(",", start) - 1
                pcode = detail[start:end]

                start = detail.find("addressCountry", end)
                start = detail.find(":", start) + 3
                end = detail.find('"', start)
                ccode = detail[start:end]


                start = detail.find("latitude", end)
                start = detail.find(":", start) + 3
                end = detail.find(",", start) - 1
                lat = detail[start:end]

                start = detail.find("longitude", end)
                start = detail.find(":", start) + 3
                end = detail.find('"', start)
                longt = detail[start:end]

                start = detail.find("telephone", end)
                start = detail.find(":", start) + 3
                end = detail.find('"', start)
                phone = detail[start:end]

                hours = ""
                hourlist = soup.findAll('div', {'class': 'hour'})
                for temph in hourlist:
                    #logger.info("Hours = ",temph.text)
                    hours = hours + temph.text +' '

                hours = hours.replace('\u200b','')
                #logger.info(hours)
                

                if len(street) < 4:
                    address = "<MISSING>"
                if len(title) < 3:
                    title = "<MISSING>"
                if len(city) < 3:
                    city = "<MISSING>"
                if len(state) < 2:
                    state = "<MISSING>"
                if len(pcode) < 5:
                    pcode = "<MISSING>"
                if len(phone) < 6:
                    phone = "<MISSING>"
                if len(hours) < 3:
                    hours = "<MISSING>"
                if len(lat) < 2 :
                    lat = "<MISSING>"
                if len(longt) < 2 :
                    longt = "<MISSING>"

                
                data.append([
                    url,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    ccode,
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours
                ])
                logger.info(data[p])
                p += 1

    return data



def scrape():
    data = fetch_data()
    write_output(data)

scrape()
