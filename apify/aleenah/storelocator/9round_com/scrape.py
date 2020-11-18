import csv
import re
from bs4 import BeautifulSoup
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('9round_com')


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    types = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids = []
    page_url = []
    countries = []
    res = requests.get("https://www.9round.com/kickboxing-classes/directory")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('div', {'class': 'col-md-12'})

    sa = divs[0].find_all('a')
    del sa[0]
    s = divs[1].find_all('a')
    del s[0]
    sa += s
    # logger.info(soup)
    for a in sa:
        url = "https://www.9round.com/" + a.get('href')
        try:
            res = requests.get(url)
        except:
            res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        # logger.info(url)

        # soup = BeautifulSoup(driver.page_source, 'html.parser')

        l = soup.find_all('div', {'class': 'd-block wow fadeIn city-list'})
        if l == []:
            continue
        l = l[0]
        lis = l.find_all('li')
        for li in lis:
            ca = li.find_all('a')
            del ca[0]
            for aa in ca:
                page_url.append(aa.get('href'))
    #logger.info(page_url)
    for url in page_url:
        logger.info(url)
        try:
            res = requests.get(url)
        except:
            res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        data = str(soup.find('script', {'type': 'application/ld+json'}))

        # logger.info(data)
        street.append(re.findall(r'"streetAddress": "([^"]*)"', data)[0].strip().replace('\u202a', ""))
        cities.append(re.findall(r'"addressLocality": "([^"]*)"', data)[0].strip().replace('\u202a', ""))
        states.append(re.findall(r'"addressRegion": "([^"]*)"', data)[0].strip().replace('\u202a', ""))
        zips.append(re.findall(r'"postalCode": "([^"]*)"', data)[0].strip().replace('\u202a', ""))
        timing.append(re.findall(r'"openingHours": "([^"]*)"', data)[0].strip().replace('\u202a', "").replace("Mo",
                                                                                                              "Monday").replace(
            "Tu", "Tuesday").replace("We", "Wednesday").replace("Th", "Thursday").replace("Fr", "Friday").replace("Sa",
                                                                                                                  "Saturday").replace(
            "Su", "Sunday"))
        if re.findall(r'"addressCountry": "([^"]*)"', data)[0] == "Canada":
            countries.append('CA')
        else:
            countries.append('US')
        locs.append(re.findall(r'"name": "([^"]*)"', data)[0].strip().replace('\u202a', ""))
        lat.append(re.findall(r'"latitude": "([^"]*)"', data)[0].strip().replace('\u202a', ""))
        long.append(re.findall(r'"longitude": "([^"]*)"', data)[0].strip().replace('\u202a', ""))
        m = soup.find_all('div', {'class': 'd-flex justify-content-center flex-column flex-lg-row mb-3'})
        if m == []:
            ids.append("<MISSING>")
            phones.append("<MISSING>")
            continue
        m = m[0]
        """but = m.find_all('button')
        if but==[]:
            but="<MISSING>"
        else:
            but=but[0].get('data-url')
            but=re.findall(r'franchise_id=(.*)', but)[0].replace('\u202a',"")
        ids.append(but)"""
        ph = m.find_all('a')
        if ph != []:
            ph = ph[0].text.strip().replace('\u202a', "")
            if "or" in ph:
                ph = ph.split("or")[0].strip()

        # logger.info(ph)
        if ph == "" or ph == []:
            ph = "<MISSING>"
        phones.append(ph)
        """l=soup.find_all('h2', {'class': 'h2-responsive card-title h1 red-text font-weight-bold text-uppercase'})
        if l==[]:
            street.append("<MISSING>")
            cities.append("<MISSING>")
            states.append("<MISSING>")
            zips.append("<MISSING>")
            timing.append("<MISSING>")
            phones.append("<MISSING>")
            ids.append("<MISSING>")
            lat.append("<MISSING>")
            long.append("<MISSING>")
            continue
        l=l[0]
        locs.append(l.text)
        addr=soup.find('h4', {'class': 'h4-responsive font-weight-bolder'}).text.strip().split("\n")
        street.append(addr[0])
        addr=addr[1].split(",")
        #logger.info(addr)
        cities.append(addr[0])
        addr=addr[1].strip().split()
        states.append(addr[0])
        zips.append(addr[1])
        tim=soup.find_all('ul', {'class': 'list-unstyled opening-hours'})
        if tim==[]:
            tim="<MISSING>"
        else:
            tim=tim[0].text
        #    logger.info(tim)
        timing.append(tim)

        lat.append(soup.find('div', {'id': 'map-container'}).get('data-lat'))
        long.append(soup.find('div', {'id': 'map-container'}).get('data-lng'))"""

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.9round.com")
        row.append(locs[i].replace('&amp;','&'))
        row.append(street[i].replace('&amp;','&'))
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url
        row = ["<MISSING>" if x == "" else x for x in row]
        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
