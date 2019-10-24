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
    url = 'https://www.streetcorner.com/consumer/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    soup = str(soup)
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    flag = True
    start = 0
    while flag:
        start = soup.find("var myLatLng", start)
        if start != -1:
            start = soup.find(":", start) + 2
            end = soup.find(",", start)
            lat = soup[start:end]
            start = soup.find(":", end) + 2
            end = soup.find("}", start)
            longt = soup[start:end]
            start = soup.find("content: '<strong>", end)
            start = soup.find(">", start) + 1
            end = soup.find("<", start)
            title = soup[start:end]
            start = soup.find("br>", start) + 3
            end = soup.find("<br", start)
            street = soup[start:end]
            start = soup.find("br/>", start) + 3
            end = soup.find("<br", start)
            detail = soup[start:end]
            temp = end
            start = detail.find(",")
            city = detail[1:start]
            start = start + 2
            end = detail.find(" ", start)
            state = detail[start:end]
            start = end + 1
            pcode = detail[start:len(detail)]
            start = temp
            start = soup.find("(", start)
            end = soup.find("<br", start)
            phone = soup[start:end]
            if phone.find("(map") > -1:
                start = start
                phone = "<MISSING>"
            else:
                start = end

            if len(street) < 3:
                street = "<MISSING>"
            if len(pcode) < 5:
                pcode = '0' + pcode
            if len(pcode) < 3:
                pcode = "<MISSING>"


            print(title)
            print(street)
            print(city)
            print(state)
            print(pcode)
            print(phone)
            print(lat)
            print(longt)
            print(p)
            print("....................")
            p += 1
            data.append([
                'https://www.streetcorner.com/',
                'https://www.streetcorner.com/consumer/',
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
                "<MISSING>"
            ])


        else:
            flag = False


    return data


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
