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
    url = 'https://greendragon.com/locations'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    maindiv = soup.find('div', {'class': 'locations-list'})
    repo_list = maindiv.findAll('a')
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    for repo in repo_list:
        link = repo['href']
        print(link)
        title = repo.text
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        maindiv = soup.find('div', {'class': 'location-details'})
        street = maindiv.find('meta', {'itemprop': 'streetAddress'})
        street = street['content']
        city = maindiv.find('meta', {'itemprop': 'addressLocality'})
        city = city['content']
        state = maindiv.find('meta', {'itemprop': 'addressRegion'})
        state = state['content']
        pcode = maindiv.find('meta', {'itemprop': 'postalCode'})
        pcode = pcode['content']
        lat = maindiv.find('meta', {'itemprop': 'latitude'})
        lat = lat['content']
        longt = maindiv.find('meta', {'itemprop': 'longitude'})
        longt = longt['content']
        detail = maindiv.findAll('p')
        phone = detail[1].text
        hours = detail[2].text
        phone = re.sub(pattern, "", phone)
        hours = re.sub(pattern, "", hours)
        phone = phone.replace("\n","")

       
        p += 1
        data.append([
            'https://greendragon.com/',
            link,
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
