from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('industriousoffice_com')

session = SgRequests()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    titlelist = []
    titlelist.append('none')
    url = 'https://www.industriousoffice.com/locations'
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.find('section', {'class': 'section-all-locations-v2 my-lg'}).findAll('li', {'class': 'market'})
    # logger.info("states = ",len(state_list))
    p = 0
    cleanr = re.compile(r'<[^>]+>')
    for states in state_list:
        # logger.info(states.find('a').text)
        '''if states.find('a').text.lower().find('coming soon') > -1 :
            continu
            e
        states = states.find('a')['href']
        if states.find('techspace') > -1:
            continue'''
        ##logger.info(states.find('a').text)
        statenow = states.find('a').text
        states = states.find('a')['href']
        logger.info(states)
        rr = session.get(states, headers=headers, verify=False)

        try:
            r = rr.text.split('var marketLocations = ', 1)[1].split('];', 1)[0]
            loclist = json.loads(r + ']')
            # logger.info(len(loclist))
            for loc in loclist:

                city = loc['city']
                state = loc['abbr']
                pcode = loc['zip']
                phone = loc['phone']
                street = loc['address']
                title = loc['location_title']
                lat = loc['latitude']
                longt = loc['longitude']
                status = loc["text_status"]
                if status.find('Coming') > -1:
                    continue
                ccode = 'US'
                link = loc['permalink'].replace('\\', '')
                if state == 'Wisconsin':
                    state = 'WI'
                try:
                    if len(state) < 2:
                        state = loc['state']
                except:
                    state = loc['state']
                if phone != '' and title not in titlelist:
                    titlelist.append(title)
                    data.append([
                        'https://www.industriousoffice.com/',
                        link.replace('\u202c',''),
                        title.replace('\u202c',''),
                        street.replace('\u202c',''),
                        city.replace('\u202c',''),
                        state.replace('\u202c',''),
                        pcode.replace('\u202c',''),
                        'US',
                        '<MISSING>',
                        phone.replace('\u202c',''),
                        '<MISSING>',
                        lat.replace('\u202c',''),
                        longt.replace('\u202c',''),
                        '<MISSING>'
                    ])
                    # logger.info(p,data[p])
                    p += 1

        except:

            r = rr.text.split('<script type="application/ld+json">', 1)[1].split('</script>', 1)[0]
            r = json.loads(r)
            link = states
            title = r['name']
            phone = r['telephone']
            street = r['address']['streetAddress']
            city = r['address']['addressLocality']
            state = r['address']['addressRegion']
            pcode = r['address']['postalCode']
            lat = r['geo']['latitude']
            longt = r['geo']['longitude']
            if state == 'Wisconsin':
                state = 'WI'
            if phone != '' and title not in titlelist:
                titlelist.append(title)
                data.append([
                    'https://www.industriousoffice.com/',
                    link.replace('\u202c',''),
                    title.replace('\u202c',''),
                    street.replace('\u202c',''),
                    city.replace('\u202c',''),
                    state.replace('\u202c',''),
                    pcode.replace('\u202c',''),
                    'US',
                    '<MISSING>',
                    phone.replace('\u202c',''),
                    '<MISSING>',
                    lat.replace('\u202c',''),
                    longt.replace('\u202c',''),
                    '<MISSING>'
                ])
                # logger.info(p,data[p])
                p += 1

    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
