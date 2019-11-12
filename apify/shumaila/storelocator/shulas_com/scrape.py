# https://www.shulas.com/directory-state/
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
    url = 'https://www.shulas.com/directory-state/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")


    detail1 = str(soup)
    start1 = 0
    n = 0
    flag = True
    while flag:
        start1 = detail1.find('"id"', start1)
        end1 = detail1.find('"remote_value"', start1)
        detail = detail1[start1:end1]
        if start1 == -1:
            flag = False
            break
        else:
            start1 = end1
            start = detail.find('"id"', 0)
            start = detail.find(':', start) + 2
            end = detail.find(',', start) - 1
            store = detail[start:end]

            start = detail.find('"name"', end)
            start = detail.find(':', start) + 2
            end = detail.find(',', start) - 1
            title = detail[start:end]
            start = end + 2
            start = detail.find('"address"', start)
            start = detail.find(':', start) + 2
            end = detail.find(',', start) - 1
            street = detail[start:end]
            start = end + 2
            start = detail.find('"city"', start)
            start = detail.find(':', start) + 2
            end = detail.find(',', start) - 1
            city = detail[start:end]
            start = end + 2
            start = detail.find('"state_code"', start)
            start = detail.find(':', start) + 2
            end = detail.find(',', start) - 1
            state = detail[start:end]
            start = end
            start = detail.find('"zip"', start)
            start = detail.find(':', start) + 2
            end = detail.find(',', start) - 1
            pcode= detail[start:end]
            start = end + 2
            start = detail.find('"phone"', start)
            start = detail.find(':', start) + 2
            end = detail.find(',', start) - 1
            phone = detail[start:end]
            start = end + 2
            start = detail.find('"long"', start)
            start = detail.find(':', start) + 1
            end = detail.find(',', start) - 1
            longt = detail[start:end]
            start = end + 2
            start = detail.find('"lat"', start)
            start = detail.find(':', start) + 1
            end = detail.find(',', start) - 1
            lat = detail[start:end]
            start = end + 2
            start = detail.find('"link"', start)
            start = detail.find(':', start) + 2
            end = detail.find(',', start) - 1
            link = detail[start:end]
            link = link.replace('\/', '/')
            if link.find("http") == -1:
                link = "https://www.shulas.com" + link
            page = requests.get(link)
            soup = BeautifulSoup(page.text, "html.parser")
            try:
                hours = soup.find('div', {'id': 'hours-location'}).text
            except:
                try:
                    hour = soup.find('div', {'class': 'wpb_text_column wpb_content_element'})
                    hours = hour.find('div', {'class':'wpb_wrapper'}).text
                    #print(len(hours))
                    if len(hours) < 4:
                        hour = hour.find('div', {'class': 'wpb_wrapper'})
                        spans = hour.findAll('span')
                        hours = spans[0].text + " " + spans[1].text
                except:

                    try:
                        hours = soup.find('div', {'class': 'hours'}).text

                    except:

                        hours = "<MISSING>"


            hours = str(hours)
            hours = hours.encode('ascii', 'ignore').decode('ascii')
            title = title.encode('ascii', 'ignore').decode('ascii')
            hours = re.sub(pattern, " ", hours)
            hours = hours.replace("\n", " ")
            hours = hours.lstrip()
            if hours.find("Hours vary depending on flight schedules") > -1:
                hours = "<MISSING>"
            title = title.lstrip()

            lat= lat.replace('"',"")
            longt = longt.replace('"', "")

            print(link)
            #print(store)
            #print(title)
            #print(street)
            #print(city)
            #print(state)
            #print(pcode)
            #print(phone)
            #print(hours)
            #print(lat)
            #print(longt)


            n += 1
            print(n)
            #print("...........................")
            data.append([
                'https://www.shulas.com/',
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

