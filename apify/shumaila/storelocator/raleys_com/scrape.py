# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-notifications")
    return webdriver.Chrome('chromedriver', chrome_options=options)
    #return webdriver.Chrome('/Users/Dell/local/chromedriver', chrome_options=options)

def fetch_data():
    # Your scraper here
    data = []


    url = 'https://www.raleys.com/store-locator/?search=all'
    driver1 = get_driver()
    driver1.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver1.page_source, "html.parser")

    repo_list = soup.findAll('li', {'class': 'marker'})


    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    p = 1
    for repo in repo_list:
        link = repo.find('a',{'class':'btn btn-hollow'})
        link = link['href']
        print(link)
        title = repo.find('h2').text
        address = repo.find('address').text
        address = re.sub(pattern, " ", address)
        phone = repo.find('a').text
        hours = repo.find('div', {'class': 'box'}).text
        hours = re.sub(pattern," ", hours)
        hours = hours.replace("\n", "")
        phone = re.sub(pattern,"",phone)

        lat = repo['data-lat']
        longt = repo['data-lng']
        print(address)
        address = usaddress.parse(address)

        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        ccode = ""

        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                    temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1 or temp[1].find("LandmarkName") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            if temp[1].find("CountryName") != -1:
                ccode = "US"
            i += 1

        street = street.lstrip()
        city = city.lstrip()
        state = state.lstrip()
        state = state.replace(",","")
        street = street.replace(",","")
        city = city.replace(",","")
        pcode = pcode.lstrip()
        if len(phone) < 5:
            phone = "<MISSING>"
        print(title)

        print(street)
        print(city)
        print(state)
        print(pcode)
        print(phone)
        print(lat)
        print(longt)
        print(hours)
        print(p)
        p += 1
        print(("............................."))
        data.append([
            'https://www.raleys.com/',
            link,
            title,
            street,
            city,
            state,
            pcode,
            "US",
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
