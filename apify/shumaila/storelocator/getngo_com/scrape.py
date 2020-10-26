# https://orthodontist.smiledoctors.com/
# https://www.getngo.com/locations/

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

    data = []
    pattern = re.compile(r'\s\s+')
    url = 'https://www.getngo.com/locations/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    maind = soup.find('div',{'class':'ccm-block-styles'})
    link_list = maind.findAll('a')
    print(len(link_list))
    for alink in link_list:

        link = "https://www.getngo.com/" + alink['href']

        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        maindiv = soup.find('div',{'class': 'ccm-layout-2-col-1 ccm-layout-cell ccm-layout-col ccm-layout-col-1 first'})
        title = maindiv.find('h2').text
        address1 = maindiv.find('h3')
        start = title.find("#") + 1
        store = title[start:len(title)]
        try:
            address = address1.findAll('span')
            street = address[0].text
            city = address[1].text
            state= address[2].text
            try:
                pcode =  address[3].text
                if len(pcode) < 4:
                    try:
                        pcode = address[4].text
                    except:
                        pcode = "<MISSING>"

            except:
                pcode = "<MISSING>"

        except:
            address = address1.text
            start = address.find("Street")
            if start != -1:
                start = address.find(' ', start)
                street = address[0:start]
                start = start + 1
                end = address.find(',', start)
                city = address[start:end]
                start = end + 2
                end = address.find(' ', start)
                if end == -1:
                    end = len(address)
                    state = address[start:end]
                    pcode = "<MISSING>"
                else:
                    state = address[start:end]
                    start = end + 1
                    end = address.find(' ', start)
                    pcode = address[start:end]

        maindiv = soup.find('div',{'class': 'ccm-layout-col-spacing'})
        maindiv = maindiv.findAll('p')
        phone = maindiv[1].text
        phone = phone.replace("Phone: ","")
        hours = maindiv[3].text
        hours = hours.replace("Hours: ","")

        soup = str(soup)
        start = soup.find("latlng",0)
        start = soup.find("(", start) + 1
        end = soup.find(",", start)
        lat = soup[start:end]
        start = end + 2
        end = soup.find(")", start)
        longt = soup[start:end]



        city = city.replace(",","")
        print(link)
        print(store)
        print(title)
        print(address1)
        print(street)
        print(city)
        print(state)
        print(pcode)
        print(phone)
        print(hours)
        print(lat)
        print(longt)
        data.append([
            'https://www.getngo.com/',
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

