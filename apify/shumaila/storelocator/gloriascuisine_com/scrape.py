# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import string
import re


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    url = 'https://gloriascuisine.com/locations/index.html'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    repo_list = soup.findAll('script', {'type': 'application/ld+json'})
    coordlist =  soup.findAll('li', {'class': 'location-list__item js-location-list-item'})
    titlelist = soup.findAll('p', {'class': 'location-city'})

    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    p = 1
    for n in range(0,len(repo_list)):

        detail = str(repo_list[n])


        start = detail.find('"telephone"')
        start = detail.find(':', start) + 3
        end = detail.find('"', start)
        phone = detail[start:end]
        start = detail.find('"streetAddress"')
        start = detail.find(':', start) + 3
        end = detail.find('"', start)
        street = detail[start:end]
        start = detail.find('"addressLocality"')
        start = detail.find(':', start) + 3
        end = detail.find('"', start)
        city = detail[start:end]
        start = detail.find('"addressRegion"')
        start = detail.find(':', start) + 3
        end = detail.find('"', start)
        state = detail[start:end]
        start = detail.find('"postalCode"')
        start = detail.find(':', start) + 3
        end = detail.find('"', start)
        pcode = detail[start:end]
        start = detail.find('"addressCountry"')
        start = detail.find(':', start) + 3
        end = detail.find('"', start)
        ccode = detail[start:end]
        hours = ""
        flag = True
        while flag:
            start = detail.find('"dayOfWeek"', end)

            if start == -1:
                flag = False
            else:
                start = detail.find('[', start) + 1
                end = detail.find(']', start)
                day = detail[start:end]
                start =  detail.find(',', end)
                end = detail.find('}', start)
                hours = hours + day + " " + detail[start:end] + " | "
                hours = re.sub(pattern,"",hours)

        hours = hours.replace('"', "")
        hours = hours.replace(',', " ")

        title = titlelist[n].text
        lat = coordlist[n]['data-coords-lat']
        longt = coordlist[n]['data-coords-lng']

        print(title)
        print(street)
        print(city)
        print(state)
        print(pcode)
        print(ccode)
        print(phone)
        print(lat)
        print(longt)
        print(hours)
        print(p)
        print("...............................")
        p += 1
        data.append([
            'https://gloriascuisine.com/',
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

    return data



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
