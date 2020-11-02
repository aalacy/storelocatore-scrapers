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
        writer.writerow(["locator_domain","page_url",  "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    p = 1
    url = 'https://greensnaturalfoods.com/Home/Location'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    repo_list = soup.findAll('div', {'class': 'col-md-5'})

    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    for repo in repo_list:
        detail = str(repo.find('p'))
        start = detail.find("<b", 0)
        start = detail.find(">", start) + 1
        end = detail.find("<", start)
        title = detail[start:end]
        start = detail.find("/>", start) + 3
        end = detail.find("<", start)
        street = detail[start:end]
        street = re.sub(pattern, "", street)
        start = detail.find("/>", start) + 3
        end = detail.find("<", start)
        rest = detail[start:end]
        start = detail.find("/>", start) + 3
        end = detail.find("<", start)
        phone = detail[start:end]
        phone = re.sub(pattern, "", phone)
        start = detail.find("/b>", start) + 3
        end = detail.find("</br", start)
        hours = detail[start:end]
        hours = re.sub(pattern,"",hours)
        start = rest.find(",")
        city = rest[0:start]
        city = re.sub(pattern,"", city)
        start = start + 2
        state = rest[start:start+2]
        start = start + 3
        pcode = rest[start:len(rest)]

        detail = repo.find('div',{'class':'tt-contact-map map-block'})
        lat = detail['data-lat']
        longt = detail['data-lng']


        p += 1
        data.append([
            'https://greensnaturalfoods.com/',
            url,
            title,
            street,
            city,
            state,
            pcode,
            'US',
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
