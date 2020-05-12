import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


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


session = SgRequests()
all = []


def fetch_data():
    # Your scraper here
    page_url = []
    res = session.get("https://www.starbuds.us/locations")
    soup = BeautifulSoup(res.text, 'html.parser')
    sa = soup.find_all('a', {'class': 'g-transparent-a b1link'})
    urls = []
    for a in sa:
        # print(a.get('href'))
        res = session.get(a.get('href'))
        soup = BeautifulSoup(res.text, 'html.parser')
        stores = soup.find_all('div', {'role': 'gridcell'})
        if len(stores) == 0:
            urls.append(a.get('href'))
        else:

            for store in stores:
                urls.append(store.find_all('a')[1].get('href'))

    for url in urls:
        print(url)
        if "starbuds.us" not in url:
            continue
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            loc = soup.find_all('h1')[1].text
        except:
            loc = soup.find_all('h1')[0].text
        loc = loc.split('\n')[-1]
        ps = soup.find_all('p', {'class': 'font_7'})
        addr = ps[0].text.replace(u'\xa0', ' ').split('-')
        street = addr[0]
        addr = addr[1].split(",")
        city = addr[0].strip()
        addr = addr[1].strip().split(" ")
        # print(addr)
        state = addr[0]
        zip = addr[1]
        phone = ps[1].text
        tim = soup.find_all('div', {'class': 'txtNew'})[3].text
        if 'HOURS' in tim:
            tim = tim.replace('HOURS', '').replace('\n', ' ').replace(u'\xa0', ' ')
        else:
            tim = soup.find_all('div', {'class': 'txtNew'})[4].text.replace('HOURS', '').replace('\n', ' ').replace(
                u'\xa0', ' ')

        try:
            lat, long = re.findall(r'/@(-?[\d\.]+),(-?[\-\d\.]+),', str(soup))[0]
        except:
            lat = long = "<INACCESSIBLE>"

        all.append([
            "https://www.starbuds.us",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim.strip(),  # timing
            url])
        # print(all)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
