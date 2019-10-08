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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    p = 1
    url = 'https://www.sephora.com/happening/storelist'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    repo_list = soup.findAll('a', {'class': 'css-j9u336'})
    cleanr = re.compile('<.*?>')
    phoner = re.compile('(.*?)')
    for repo in repo_list:
        link = "https://www.sephora.com" + repo['href']
        # link = "https://www.sephora.com/happening/stores/silverdale-jcpenney-at-kitsap-mall"
        print(link)
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        detail = soup.find('script', {'type': 'application/ld+json'})
        detail = str(detail)
        print(detail)
        if detail == "None":
            detail = str(soup)
        start = detail.find("streetAddress")
        start = detail.find(":", start) + 2
        end = detail.find(",", start) - 1
        street = detail[start:end]
        start = street.find('\\')
        if start != -1:
            street = street.replace("\\", "!")
            street = street.replace("!n"," ")
        street = street.replace("\n", " ")

        start = detail.find("postalCode")
        start = detail.find(":", start) + 2
        end = detail.find(",", start) - 1
        pcode = detail[start:end]
        start = pcode.find("O")
        if start != -1:
            pcode = pcode.replace("O", "0")
        start = detail.find("telephone")
        start = detail.find(":", start) + 2
        end = detail.find(",", start) - 1
        phone = detail[start:end]

        start = detail.find("addressLocality")
        start = detail.find(":", start) + 2
        end = detail.find(",", start) - 1
        city = detail[start:end]

        start = detail.find("addressRegion")
        start = detail.find(":", start) + 2
        end = detail.find("}", start) - 1
        state = detail[start:end]

        start = detail.find("name")
        start = detail.find(":", start) + 2
        end = detail.find(",", start) - 1
        title = detail[start:end]
        start = detail.find("openingHours")
        start = detail.find("[", start) + 2
        end = detail.find("]", start) - 1
        hours = detail[start:end]
        hours = hours.replace('"', "")
        hours = hours.replace(',', " | ")
        detail = str(soup)
        start = detail.find("latitude")
        start = detail.find(":", start) + 1
        end = detail.find(",", start) - 1
        lat = detail[start:end]
        start = detail.find("longitude")
        start = detail.find(":", start) + 1
        end = detail.find(",", start)
        longt = detail[start:end]

        detail = str(soup)
        start = detail.find("storeInfo")
        start = detail.find("country",start)
        start = detail.find(":", start) + 2
        end = detail.find(",", start)-1
        ccode = detail[start:end]
        try:

            start = detail.find("isOnlineReservationEnabled")
            start = detail.find("storeId",start)
            start = detail.find(":", start) + 2
            end = detail.find(",", start) - 1
            store = detail[start:end]
        except:
            store = "<MISSING>"
        street = re.sub('\n', " ", street)
        if len(title) < 3:
            title = "<MISSING>"
        if len(street) < 3:
            street = "<MISSING>"
        if len(city) < 3:
            city = "<MISSING>"
        if len(ccode) < 2:
            ccode = "<MISSING>"
        if len(pcode) < 5:
            pcode = "<MISSING>"
        if len(store) < 2:
            store = "<MISSING>"
        if len(phone) < 5:
            phone = "<MISSING>"
        if len(hours) < 4:
            hours = "<MISSING>"
        if len(lat) < 2:
            lat = "<MISSING>"
        if len(longt) < 2:
            longt = "<MISSING>"
        if hours.find("image:") > -1 or hours.find("url:") > -1:
            hours = "<MISSING>"
        if len(store) < 3 or len(store) > 10:
            store = "<MISSING>"
        if state == "NW":
            state = "WA"

        print(p)
        print(title)
        print(street)
        print(city)
        print(state)
        print(ccode)
        print(pcode)
        print(phone)
        print(store)
        print(hours)
        print(lat)
        print(longt)

        print("................")

        flag = 0
        for chk in data:
            if chk[2] == street:
                flag = 1
                print("Already exist")
                break

        if flag == 0:
            data.append([
                url,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours
            ])
        p += 1

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
