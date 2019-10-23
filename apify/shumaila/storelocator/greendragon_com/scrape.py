# Import libraries
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

        title = repo.text
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        maindiv = soup.find('div', {'class': 'location-details'})


        detail = maindiv.findAll('p')
        address = detail[0].text
        address = re.sub(pattern,"", address)
        address = address.lstrip()
        if address.find("(") > -1:
            address = address[0:address.find("(")]
        address = usaddress.parse(address)

        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                    temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        try:
            frames = soup.find('iframe')
            coord = str(frames['src'])
            start = coord.find('!1d') + 3
            end = coord.find('!2d', start)
            lat = coord[start:end]
            start = end + 3
            end = coord.find('!3f', start)
            longt = coord[start:end]
            lat = lat[0:8]
            longt = longt[0:10]
        except:
            lat = "<MISSING>"
            longt = "<MISSING>"



        phone = detail[1].text
        hours = detail[2].text
        phone = re.sub(pattern, "", phone)
        hours = re.sub(pattern, "", hours)
        phone = phone.replace("\n","")
        street = street.lstrip()
        city = city.lstrip()
        city = city.replace(",", "")
        state = state.lstrip()
        pcode = pcode.lstrip()





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
