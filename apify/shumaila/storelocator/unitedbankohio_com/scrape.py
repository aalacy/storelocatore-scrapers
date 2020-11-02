import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('unitedbankohio_com')




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
    p = 1
    pattern = re.compile(r'\s\s+')
    url = 'https://unitedbankohio.com/locations/?place&latitude&longitude&type=location#038;latitude&longitude&type=location'
    flag = True
    while flag:
        #logger.info(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        divlist = soup.findAll('div',{'class':'location-list-result'})
        coord = str(soup.find('div', {'class':'map_container'}))
        lats = []
        longts = []
        start = 0
        while True:
            start = coord.find('"lat"', start)
            if start == -1:
                break
            else:
                start = coord.find(':', start) + 2
                end = coord.find('"', start)
                lat = coord[start:end]
                lats.append(lat)
                start = coord.find('"lng"', end)
                start = coord.find(':', start) + 2
                end = coord.find('"', start)
                longt = coord[start:end]
                longts.append(longt)


        i = 0
        for div in divlist:
            title = div.find('span',{'class':'sub-head fw-light'}).text
            address= str(div.find('span',{'class':'branch-address fw-light'}))
            address = re.sub(pattern,"",address)
            phone = div.find('div', {'class': 'large-8 columns'}).find('a').text
            try:
                hours = div.find('div', {'class': 'large-6 small-6 columns'}).text
            except:
                hours = "<MISSING>"
            bank = div.find('span',{'class': 'branch-name'}).text
            title = bank + " | " + title
            stored = div.find('div', {'class': 'links fw-light'})
            stored = stored.findAll('a')
            store = stored[1]['data-locationid']

            lat = lats[i]
            longt = longts[i]
            i += 1
            title = re.sub(pattern,"",title)
            hours = hours.replace("\n","")
            title = title.replace("\n", " ")
            title = title.strip()
            start = address.find(">")+1
            end = address.find("<br",start)
            street = address[start:end]
            start = address.find(">",end)+1
            end = address.find(",", start)
            city = address[start:end]
            start = end + 2
            end = address.find(" ", start)
            state = address[start:end]
            start = end + 1
            end = address.find("<br", start)
            pcode = address[start:end]
            if phone.find("Get Directions") > -1:
                phone = "<MISSING>"

            try:
                ltyped = div.find('div', {'class': 'large-4 columns'}).text
                ltyped = ltyped.replace("\n", "|")
                ltype = ltyped[1:len(ltyped)]

                m = 0
                temp = ""
                while m < len(ltype):
                    end = ltype.find("|", m)
                    if ltype[m:end].find("Branch") > - 1 or ltype[m:end].find("ATM") > - 1:
                        if len(temp) > 1:
                            temp = temp + "|"
                        temp = temp + ltype[m:end]
                    m = end + 1

                ltype = temp
                # logger.info(ltype)
            except:
                ltype = "<MISSING>"
            if len(pcode)<5:
                pcode = '0' + pcode


            #logger.info(url)
            #logger.info(title)
            #logger.info(store)
            #logger.info(ltype)
            #logger.info(address)
            #logger.info(street)
            #logger.info(city)
            #logger.info(state)
            #logger.info(pcode)
            #logger.info(hours)
            #logger.info(phone)
            #logger.info(lat)
            #logger.info(longt)
            #logger.info(p)
            #logger.info(".......................")
            p += 1
            data.append([
                'https://unitedbankohio.com/',
                url,
                title,
                street,
                city,
                state,
                pcode,
                'US',
                store,
                phone,
                ltype,
                lat,
                longt,
                hours
            ])

        next = soup.find('a', {'class': 'next page-numbers'})
        try:

            url = next['href']

        except:
            flag = False

    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()

