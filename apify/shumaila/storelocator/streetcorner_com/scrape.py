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
    start1 = 0
    while flag:
        start = soup.find("www.streetcorner.com/store/", start)
        start1 = soup.find("var myLatLng", start1)
        if start != -1 and start1 != -1:
            start1 = soup.find(":", start1) + 2
            end1 = soup.find(",", start1)
            lat = soup[start1:end1]
            start1 = soup.find(":", end1) + 2
            end1 = soup.find("}", start1)
            longt = soup[start1:end1]
            start1 = end1

            start = soup.find("store/", start)
            start = soup.find("/", start)+1
            end= soup.find('"', start)
            link = "http://www.streetcorner.com/store/" + soup[start:end]
            print(link)
            page = requests.get(link)
            soup1 = BeautifulSoup(page.text, "html.parser")
            title = soup1.find('span',{'itemprop':'name'}).text
            try:
                street = soup1.find('span', {'itemprop': 'streetAddress'}).text
            except:
                street = "<MISSING>"
            try:
                city = soup1.find('span', {'itemprop': 'addressLocality'}).text
            except:
                city = "<MISSING>"
            try:
                state = soup1.find('span', {'itemprop': 'addressRegion'}).text
            except:
                state = "<MISSING>"
            try:
                pcode = soup1.find('span', {'itemprop': 'postalCode'}).text
            except:
                pcode = "<MISSING>"
            try:
                phone = soup1.find('span', {'itemprop': 'telephone'}).text
            except:
                phone = "<MISSING>"
            try:
                hours = soup1.find('span', {'itemprop': 'openingHours'}).text
            except:
               hours = "<MISSING>"
            if len(phone) < 3:
                phone = "<MISSING>"
            if len(street) < 2:
                street = "<MISSING>"
            if len(pcode) < 2:
                pcode = "<MISSING>"
            else:
                if len(pcode) == 4:
                    pcode = '0' + pcode

            hours = hours.encode('ascii', 'ignore').decode('ascii')
            #print(hours)
            p += 1
            if title.find("Coming Soon") == -1:
                data.append([
                       'https://www.streetcorner.com/',
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







        else:
            flag = False


    return data


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
