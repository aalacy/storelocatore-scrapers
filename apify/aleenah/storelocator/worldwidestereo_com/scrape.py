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
all=[]
def fetch_data():
    # Your scraper here

    res=session.get("https://www.worldwidestereo.com/pages/showrooms")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find('div', {'class': 'callout-grid__row grid grid--2-at-medium'}).find_all('div', {'class': 'callout-grid__column grid__cell'})
    for div in divs:
        url=div.find('a').get('href')
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        data = soup.find('div', {'class': 'callout-grid__row grid grid--3-at-medium'}).find_all('div', {'class': 'callout-grid__content callout-grid__content--top'})
        street,city,state,zip=re.findall(r'center">(.*)<br/>(.*), (.*) (.*)</p>',str(data[0].find('p')))[0]
        lat,long=re.findall(r'/@(-?[\d\.]+),(-?[\d\.]+)',data[0].find('a').get('href'))[0]
        phone = data[1].find('a').text
        tim=data[2].find('p').text.replace('MS','M S')
        loc=soup.find('h1').text.split('our')[-1].strip()

        all.append([
            "https://www.worldwidestereo.com",
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
            tim,  # timing
            url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
