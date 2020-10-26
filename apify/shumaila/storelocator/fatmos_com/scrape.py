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


def fetch_data():
    # Your scraper here
    data = []

    url = 'http://fatmos.com/Locations/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    divs_list = soup.findAll('div', {'class': 'news_item'})

    cleanr = re.compile('<.*?>')
    print(len(divs_list))
    for divs in divs_list:
        store = divs['id']
        title = divs.find('h3').text
        details = divs.findAll('p')
        print(len(details))
        links = divs.findAll('a')
        for link in links:
            if link.text == "Map":
                link = link['href']
                break
        if len(details) == 2:
            details = divs.text
            details = details.replace("\n", "|")
            start = details.find(" |||") + 4
            end =  details.find("Map")
            details = details[start:end]
            end = details.find("-")
            street = details[0:end]
            start = end + 2
            end = details.find(",", start)
            city = details[start:end]
            start = end + 2
            end = start + 2
            state = details[start:end]
            start = end + 1
            end = details.find("(", start)
            pcode = details[start:end]
            phone = details[end: len(details)]



        else:

            details = details[1].text
            details = details.replace("\n", "|")
            temp = details.find(",")
            temp1 = details.find("|")
            if temp < temp1:
                start = details.find("-")
                street = details[0 : start - 1]
                start = start + 1
                end = temp
                city = details[start: end]

            else:

                if details.find("|") == 0:
                    start = 2
                else:
                    start = 0

                end = details.find("|",start)
                street = details[start:end]

                start = end + 1
                end = details.find(",", start)
                city = details[start:end]
            start = end + 2
            end = start + 3
            state = details[start : end]
            start = end
            end = details.find("|" , start)
            pcode = details[start:end]
            start = end + 1
            end = len(details)
            phone = details[start:end]
            phone = phone.replace("Tel","")
            phone = phone.replace(":", "")
            phone = phone.replace("|Map", "")
            phone = phone.lstrip()

        lat = "<MISSING>"
        longt = "<MISSING>"
        link = str(link)
        start = link.find("&sll=")
        if start == -1:
            lat = "<MISSING>"
            longt  = "<MISSING>"
        else:

            start = link.find("&sll=", 0)
            print("link = ", start)
            start = link.find("=", start)
            end = link.find(",", start)
            lat = link[start+1:end]
            start = end + 1
            end = link.find("&", start)
            longt = link[start:end]

        title = title.lstrip()
        store = store.replace("news_item_", "")
        start = city.find('|')
        if start != -1:
            street = street + " " + city[0:start]
            city = city[start+1:len(city)]

        city = city.lstrip()
        print(store)
        print(title)
        print(street)
        print(city)
        print(state)
        print(pcode)
        print(phone)
        print(lat)
        print(longt)
        #print(details)
        print(link)


        print("........................")
        data.append([
            url,
            url,
            title,
            street,
            city,
            state,
            pcode,
            "US",
            store,
            phone,
            "<MISSING>",
            lat,
            longt,
            "<MISSING>"
        ])

    return data

def scrape():
        data = fetch_data()
        write_output(data)

scrape()
