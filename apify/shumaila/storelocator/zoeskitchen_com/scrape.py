import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time


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
    p = 1
    data = []

    pattern = re.compile(r'\s\s+')
    url = 'https://zoeskitchen.com/locations/sitemap'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    linklist = soup.findAll('a',{'class':'green no-underline'})
    print(len(linklist))
    for blink in linklist:
        link = "https://zoeskitchen.com/" + blink['href']
        page1 = requests.get(link)
        soup1 = BeautifulSoup(page1.text, "html.parser")
        title = soup1.find("h3", {'class': 'location-title'}).text
        address = soup1.find('div', {'class': 'address'}).text
        hours = soup1.find('table', {'class': 'hours'}).text
        address = address.replace("\n", "|")
        store = soup1.find('a', {'class': 'btn btn-default order-btn'})

        store = store['href']
        start = store.find("=") + 1
        store = store[start:len(store)]
        phone = soup1.find('a', {'class': 'tel'}).text
        soup1 = str(soup1)
        start = soup1.find("var location = ")
        start = soup1.find("lat", start) + 5
        end = soup1.find(",", start)
        lat = soup1[start:end]
        start = soup1.find("lng", end) + 5
        end = soup1.find("}", start)
        longt = soup1[start:end]
        address = address[1:len(address) - 1]
        start = address.find("|")
        street = address[0:start]
        start = start + 1
        end = address.find(",", start)
        city = address[start:end]
        start = end + 2
        end = address.find(" ", start)
        state = address[start:end]
        start = end + 1
        end = address.find("|", start)
        pcode = address[start:end]
        hours = re.sub(pattern, " ", hours)
        hours = hours.lstrip()
        if len(hours) < 3:
            hours = "<MISSING>"
        if len(phone) < 3:
            phone = "<MISSING>"

        #print(link)
        #print(title)
        #print(store)
        #print(address)
        #print(street)
        #print(city)
        #print(state)
        #print(pcode)
        #print(hours)
        #print(phone)
        #print(lat)
        #print(longt)
        #print(p)
        p += 1
        print("...........................")

        data.append([
            'https://zoeskitchen.com/',
            link,
            title,
            street,
            city,
            state,
            pcode,
            'US',
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
