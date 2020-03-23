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
    res=session.get("https://www.sbe.com/hotels/brands/ciel-spa")
    soup = BeautifulSoup(res.text, 'html.parser')

    urls=soup.find_all('li', {'class': 'cols ftr-itm box-shadow'})

    for url in urls:
        loc = url.find('h5').text
        url=url.find('a').get('href')
        #print(url)
        res=session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        street = soup.find('span', {'class': 'address1'}).text.strip()
        city = soup.find('span', {'class': 'city'}).text.replace(',', '').strip()
        state = soup.find('span', {'class': 'state'}).text.strip()
        zip = soup.find('span', {'class': 'postal_code'}).text.strip()
        tim = soup.find('div', {'class': 'text-spaced-extra more_info'}).text.replace('Order Food Delivery with DoorDash', '').replace('\n', ' ').strip()
        phone = soup.find('li', {'class': 'serif-face cols borderright'}).find('a').text.strip()
        lat = soup.find('div', {'id': 'map_canvas'}).get('data-latitude')
        long = soup.find('div', {'id': 'map_canvas'}).get('data-longitude')

        if long.strip() =="":
            long=re.findall(r'data-longitude="([^"]+)"',str(soup.find('div', {'id': 'map_canvas'})))[0]
        #print(long)
        all.append([
            "https://www.sbe.com/hotels/brands/ciel-spa",
            loc,
            street,
            city,
            state,
            zip,
            'US',
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


