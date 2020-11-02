import csv
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('saharapizza_com')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]

    res=session.get("http://saharapizza.com/store_locations.htm")
    logger.info(res)
    soup = BeautifulSoup(res.text, 'html.parser')
    #logger.info(soup)
    trs = soup.find('table', {'id': 'table2'}).find_all('tr')
    del trs[0]
    for tr in trs:
        tds=tr.find_all('td')
        if len(tds) <2:
            continue

        addr= tds[1].text.replace("\t"," ").strip()
        if "Catering" in tds[0].find('b').text.strip():
            continue
        if addr=="":
            logger.info("empty")
            cities.append("<MISSING>")
            states.append("<MISSING>")
            street.append("<MISSING>")
            zips.append("<MISSING>")
            timing.append("<MISSING>")
            locs.append(tds[0].find('b').text.strip())
        elif "CLOSED" in addr:
            continue
        else:
            title= tds[1].get('title')
            l = tds[0].find('b').text.strip().split("/")[0].strip()
            addr = re.sub(r"[ ]+",r" ",addr.replace("\r\n", "").replace("\n", ""))
         #   logger.info(addr)
            if l in title :
                #logger.info("in")
                title=title.split(",")
                sz= title[-1].strip().split(" ")
                states.append(sz[0])
                zips.append(sz[1])
                cities.append(title[-2].strip())
                street.append(title[0])

            else:
                #logger.info("not in")
                if l == "Bolivia":
                    continue

                if "Hours:" in addr:
                    addr = addr.split("Hours:")[0].strip()
                street.append(addr)
                cities.append("<MISSING>")
                states.append("<MISSING>")
                zips.append("<MISSING>")

            if "Hours:" in addr:
                timing.append(addr.split("Hours:")[1].strip())
                #logger.info(addr.split("Hours:")[1].strip())
            else:
                timing.append("<MISSING>")

            locs.append(l)

        ph = re.findall(r'([\(\) 0-9\-]+)',tds[2].find('b').text)[0].strip()
        #logger.info(ph)
        if ph!= "":
            if len(ph) <8:
                ph = re.findall(r'([\(\) 0-9\-]+)', tds[3].find('b').text)[0].strip()
            phones.append(ph)
        else:

            phones.append(ph)

        #logger.info(tds[0].find('b').text.strip())

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("http://saharapizza.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])  # timing
        row.append("http://saharapizza.com/store_locations.htm")  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
