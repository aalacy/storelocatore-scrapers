# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
    url = 'https://www.cvsfamilyfoods.com/stores/search-stores.html'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    maindiv = soup.find('div', {'class': 'grid-x small-up-2 medium-up-4 large-up-8 find-view-states'})
    repo_list= maindiv.findAll('div', {'class': 'cell'})

    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    for repo in repo_list:
        link = repo.find('a')
        link = "https://www.cvsfamilyfoods.com" + link['href']
        #print(link)
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        mainav = soup.find('nav', {'class': 'standardPagination'})
        mainul = mainav.find('ul')
        page_list = mainul.findAll('li')
        for n in range(1,len(page_list)):

            plink = link + "&displayCount=6&currentPageNumber=" + str(n)
            print(link)
            print(plink)
            page1 = requests.get(plink)
            soup1 = BeautifulSoup(page1.text, "html.parser")
            maind = soup1.find('div', {'id': 'store-search-results'})
            mainul = maind.find('ul')

            lilist = mainul.findAll('li')
            print(len(lilist))
            for detail in lilist:
                detail = str(detail)
                if detail.find('data-storeid') > -1:
                    start = detail.find('data-storeid')
                    start = detail.find('=', start) + 2
                    end = detail.find('"', start)
                    store = detail[start:end]
                    start = detail.find('data-storelat')
                    start = detail.find('=', start) + 2
                    end = detail.find('"', start)
                    lat = detail[start:end]
                    start = detail.find('data-storelng')
                    start = detail.find('=', start) + 2
                    end = detail.find('"', start)
                    longt = detail[start:end]
                    start = detail.find('store-display-name')
                    start = detail.find('>', start) + 1
                    end = detail.find('<', start)
                    title = detail[start:end]
                    start = detail.find('store-address')
                    start = detail.find('>', start) + 1
                    end = detail.find('<', start)
                    street = detail[start:end]
                    start = detail.find('store-city-state-zip')
                    start = detail.find('>', start) + 1
                    end = detail.find('<', start)
                    address = detail[start:end]
                    start = address.find(",")
                    city = address[0:start]
                    start = start + 2
                    end = start + 2
                    state = address[start:end]
                    start = start + 3
                    end = len(address)
                    pcode = address[start:end]
                    start = detail.find('Store Hours')
                    start = detail.find('<li>', start) + 5
                    end = detail.find('</', start)
                    hours = detail[start:end]
                    hours = re.sub(pattern," ", hours)
                    start = detail.find('show-for-medium')
                    start = detail.find('>', start) + 1
                    end = detail.find('<', start)
                    phone = detail[start:end]

                    hours = hours.replace(",", "|")
                    hours = hours[1:len(hours)]

                    print(title)
                    print(store)

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
                    print('..................')
                    data.append([
                        'https://www.cvsfamilyfoods.com/',
                        plink,
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
