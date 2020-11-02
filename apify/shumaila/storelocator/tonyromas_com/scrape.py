import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tonyromas_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


data = []
endprint = []
total = 0
url = 'https://locations.tonyromas.com/'

def fetch_data():
    temp1 =loadmain("https://locations.tonyromas.com/united-states")
    temp2 =loadmain("https://locations.tonyromas.com/canada")

    logger.info(temp1)
    logger.info(temp2)
    logger.info(endprint)
    return data
    # Your scraper here




def loadmain(mainlink):
    b = 1
    s = 1
    c = 1
    missing = 0

    page = requests.get(mainlink)
    soup = BeautifulSoup(page.text, "html.parser")
    state_list = soup.findAll('a', {'class': 'Directory-listLink'})



    for states in state_list:
        if states['href'].find('/') == 0:
            states = "https://locations.tonyromas.com" + states['href']
        else:
            states = "https://locations.tonyromas.com/" + states['href']
        #logger.info("loop1")
        logger.info(states)
        page = requests.get(states)
        c = 1
        soup = BeautifulSoup(page.text, "html.parser")
        repo_list = soup.findAll('a', {'class': 'Directory-listLink'})
        if len(repo_list) == 0:
            repo_list = soup.findAll('a', {'class': 'Teaser-titleLink Link--body'})

        if len(repo_list) == 0:
            data = extractinfo(states, soup)
            b += 1

        else:
            for cities in repo_list:
                cities = cities['href']
                cities = cities.replace("..", "")
                if cities.find('/') == 0:
                    cities = "https://locations.tonyromas.com" + cities
                else:
                    cities = "https://locations.tonyromas.com/" + cities
                logger.info(cities)

                page = requests.get(cities)

                soup = BeautifulSoup(page.text, "html.parser")
                try:
                    geo = soup.find('span', {'class': 'coordinates'})
                    coord = geo.findAll('meta')
                    logger.info("loop2")
                    #logger.info("state = ", s, " cities = ", c, " branch= ", b)
                    data = extractinfo(cities, soup)
                    b += 1
                except:

                    branches = soup.findAll('a', {'class': 'Teaser-titleLink Link--body'})

                    if len(branches) > 0:
                        logger.info("loop3")

                        for branch in branches:
                            #branch = branch.find('a', {'class': 'Teaser-titleLink Link--body'})
                            blink = branch['href']

                            blink = blink.replace("..", "")
                            blink = blink.replace("//","/")
                            blink = "https://locations.tonyromas.com" + blink
                            logger.info(blink)
                            page = requests.get(blink)
                            soup = BeautifulSoup(page.text, "html.parser")
                            try:
                                logger.info("loop4")
                                geo = soup.find('span', {'class': 'coordinates'})
                                coord = geo.findAll('meta')
                                nut = str(soup)
                                if nut.find("404 page not found.") == -1:
                                    logger.info("ENTER")
                                    data = extractinfo(blink, soup)
                                    b += 1
                                else:
                                    logger.info("404 page not found.")
                                    logger.info(cities)
                                    missing += 1
                            except:
                                logger.info("loop5")
                                inter = soup.findAll('a', {'class': 'Teaser-titleLink Link--body'})
                                #logger.info("brancccccccccccccccccccccccch")
                                for binter in inter:
                                    blink = binter['href']
                                    blink = blink.replace("../", "")
                                    if blink.find('/') == 0:
                                        blink = "https://locations.tonyromas.com" + blink
                                    else:
                                        blink = "https://locations.tonyromas.com/" + blink

                                    logger.info(blink)
                                    page = requests.get(blink)
                                    soup = BeautifulSoup(page.text, "html.parser")
                                    temp = str(soup)
                                    if tem.find("404 page not found.") == -1:
                                        data = extractinfo(blink,soup)
                                        b += 1
                                    else:
                                        logger.info("404 page not found.")
                                        missing += 1

                    else:
                        logger.info("404 page not found.")
                        missing += 1



                c += 1

            temp = b - 1
            endprint.append([states, temp])
            s += 1




    prstr = "total Branches = " + str(temp)
    return prstr



def extractinfo(link, soup):

    geo = soup.find('span', {'class': 'coordinates'})
    coord = geo.findAll('meta')
    lat = coord[0]['content']
    longt = coord[1]['content']
    hdetail = soup.find('span', {'class': 'LocationName'})
    title = hdetail.text
    hdetail = soup.find('address', {'class': 'c-address'})
    address = hdetail.findAll('meta')
    city = address[0]['content']
    street = address[1]['content']
    address = hdetail.findAll('abbr')
    state = address[0].text
    ccode = address[1].text
    address = hdetail.find('span', {'class': 'c-address-postal-code'})
    pcode = address.text
    address = soup.find('span', {'id': 'telephone'})
    phone = address.text
    try:
        table = soup.find('table', {'class': 'c-location-hours-details'})
        trows = table.findAll('tr')
        hours = ""
        for row in trows:
            hours = hours + "|" + row.text
        start = hours.find("WeekHours")
        start = hours.find("|", start) + 1
        hours = hours[start:len(hours)]
    except:
        hours = "<MISSING>"
    hdetail = str(soup)
    start = hdetail.find('"id"')
    start = hdetail.find(':', start) + 1
    end = hdetail.find(',', start)
    store = hdetail[start:end]

    soup = str(soup)
    ltype = ""
    start = soup.find("ATM")
    if start == -1:
        ltype = "Branch"
    else:
        ltype = "Branch | ATM"


    logger.info(title)
    logger.info(store)
    #logger.info(ltype)
    logger.info(street)
    logger.info(city)
    logger.info(state)
    logger.info(pcode)
    logger.info(ccode)
    logger.info(phone)
    logger.info(lat)
    logger.info(longt)
    logger.info(hours)
    logger.info('..................')



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
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
