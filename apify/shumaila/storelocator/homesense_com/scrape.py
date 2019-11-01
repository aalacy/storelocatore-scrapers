import requests
from bs4 import BeautifulSoup
import csv
import string
import re
import usaddress


def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    p = 1
    #shopvgs.com
    url = 'https://us.homesense.com/locator'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    #print(soup)
    repo_list = soup.findAll('div',{'class':'store-list'})

    soup = str(soup)
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    for repo in repo_list:
        state = repo.find("h5").text
        start = state.find(",")
        city = state[0:start]
        start = start + 2
        state = state[start:len(state)]

        address = repo.find('span',{'class':'grey-txt'}).text
        address = re.sub(pattern,"|",address)

        address = address[1:len(address)-1]
        start = address.find("|")
        title = address[0:start]
        start = start + 1
        end = address.find("|",start)
        street = address[start:end]
        start = address.find(state)
        start = address.find(" ", start) + 1
        end = address.find("\n", start)
        pcode = address[start:end]
        try:
            phone = repo.find('a').text
        except:
            phone = "<MISSING>"
        try:
            hours = repo.find('strong').text
            hours = re.sub(pattern,"|",hours)
            hours = hours[1:len(hours)-1]
        except:
            hours = "<MISSING>"


        #print(address)
        #print(title)
        #print(street)
        #print(city)
        #print(state)
        #print(pcode)
        #print(phone)
        #print(hours)
        #print(".................")
        data.append([
            'https://us.homesense.com/',
            'https://us.homesense.com/locator',
            title,
            street,
            city,
            state,
            pcode,
            'US',
            "<MISSING>",
            phone,
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
            hours
        ])



    return data


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
