import requests
from bs4 import BeautifulSoup
import csv
import string
import re
import usaddress


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    url = 'https://www.independentbank.com/all-locations?type=All'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    maindiv = soup.find('div', {'class': 'location-list'})
    repo_list = maindiv.findAll('div', {'class': 'listed-item'})
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    for repo in repo_list:
        title = repo.find('h4').text
        start = title.find("|")
        title = title[0:start-1]
        print(title)
        ltype = repo.find('strong').text
        start = ltype.find(" ")
        ltype = ltype[0:start]
        print(ltype)
        address = repo.find('p').text
        address = re.sub(pattern, "", address)
        address = re.sub("\n", "|", address)
        start = address.find("|")
        phone = address[start+4:len(address)-1]
        print(phone)
        address = address[3:start]

        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]

            i += 1

        htemp = repo.find('div', {'class': 'hours'})
        hours = htemp.findAll('p')
        try:
            hours = hours[1].text
        except:
            hours = "<MISSING>"

        print(hours)
        ltemp = repo.find('div', {'class': 'item-links'})
        id = ltemp.find('span')
        id = id['data-location']
        print(id)
        alink = ltemp.find('a')
        alink = alink['href']

        start = alink.find("destination")
        lat = "N/A"
        longt = "N/A"

        if start != -1:
            start = alink.find("=", start)
            end = alink.find(",", start)
            lat = alink[start+1:end]
            longt = alink[end+1:len(alink)]

        street = street.lstrip()
        city = city.lstrip()
        city = city.replace(",","")
        pcode = pcode.lstrip()
        state = state.strip()
        phone = phone.replace(".","-")
        if ltype.find("ATM") > -1:
            ltype = "ATM"
        else:
            ltype = "Branch"
        if len(street) < 4:
            street = "<MISSING>"
        if len(city) < 3:
            city = "<MISSING>"
        if len(state) < 2:
            state = "<MISSING>"
        if len(pcode) < 5:
            pcode = "<MISSING>"
        if len(phone) < 5:
            phone = "<MISSING>"
        if len(id) < 5:
            id = "<MISSING>"

        print(street)
        print(city)
        print(state)
        print(pcode)
        print(lat)
        print(longt)
        data.append([
            url,
            title,
            street,
            city,
            state,
            pcode,
            "US",
            id,
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
