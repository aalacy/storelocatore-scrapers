import requests
from bs4 import BeautifulSoup
import csv
import string
import re


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


data = []
endprint = []

def fetch_data():
    # Your scraper here

    s = 1
    c = 1
    b = 1
    url = 'https://locations.bannerbank.com/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    state_list = soup.findAll('a', {'class': 'Directory-listLink'})

    cleanr = re.compile('<.*?>')

    for states in state_list:
        states = "https://locations.bannerbank.com/" + states['href']

        page = requests.get(states)
        c = 1
        soup = BeautifulSoup(page.text, "html.parser")
        repo_list = soup.findAll('a', {'class': 'Directory-listLink'})
        for cities in repo_list:
            cities = "https://locations.bannerbank.com/" + cities['href']


            page = requests.get(cities)
            soup = BeautifulSoup(page.text, "html.parser")
            try:
                geo= soup.find('span', {'class': 'coordinates'})
                coord = geo.findAll('meta')
                print("state = ", s, " cities = ", c, " branch= ", b)
                extractinfo(url, cities, soup)
                b += 1


            except:
                branches = soup.findAll('a', {'class': 'Teaser-titleLink Link--secondary Link--normalSecondary'})
                for branch in branches:
                    blink = branch['href']
                    blink = blink.replace("..", "")
                    blink = "https://locations.bannerbank.com/" + blink
                    page = requests.get(blink)
                    soup = BeautifulSoup(page.text, "html.parser")
                    geo = soup.find('span', {'class': 'coordinates'})
                    coord = geo.findAll('meta')
                    print("brancccccccccccccccccccccccch")
                    print("state = ", s, " cities = ", c, " branch= ", b)
                    extractinfo(url, blink, soup)

                    b += 1

            c += 1



        temp = b -1
        endprint.append([states,temp])
        s += 1

    temp = b - 1
    print("total branches = ", temp)
    print(endprint);
    return data

def extractinfo(url, link, soup):

    geo = soup.find('span', {'class': 'coordinates'})
    coord = geo.findAll('meta')
    lat = coord[0]['content']
    longt = coord[1]['content']
    hdetail = soup.find('span', {'class': 'LocationName'})
    title = hdetail.text
    hdetail = soup.find('address', {'class': 'c-address'})
    address = hdetail.findAll('meta')
    city = address[0]['content']
    street = address[1]['content']
    address = hdetail.findAll('abbr')
    state = address[0].text
    ccode = address[1].text
    address = hdetail.find('span', {'class': 'c-address-postal-code'})
    pcode = address.text
    address = soup.find('span', {'id': 'telephone'})
    phone = address.text
    table = soup.find('table', {'class': 'c-location-hours-details'})
    trows = table.findAll('tr')
    hours = ""
    for row in trows:
        hours = hours + "|" + row.text
    start = hours.find("WeekHours")
    start = hours.find("|", start) + 1
    hours = hours[start:len(hours)]
    hdetail = str(soup)
    start = hdetail.find('"id"')
    start = hdetail.find(':', start) + 1
    end = hdetail.find(',', start)
    store = hdetail[start:end]

    soup = str(soup)
    ltype = ""
    start = soup.find("ATM")
    if start == -1:
        ltype = "Branch"
    else:
        ltype = "Branch | ATM"


    print(title)
    print(store)
    print(ltype)
    print(street)
    print(city)
    print(state)
    print(pcode)
    print(ccode)
    print(phone)
    print(lat)
    print(longt)
    print(hours)
    print('..................')



    data.append([
        url,
        link,
        title,
        street,
        city,
        state,
        pcode,
        ccode,
        store,
        phone,
        ltype,
        lat,
        longt,
        hours
    ])
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
