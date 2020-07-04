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
    p = 0
    url = 'https://www.flightfitnfun.com/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    mainul = soup.find('ul', {'class': 'r3-location__list'})
    li_list = mainul.findAll('li')

    cleanr = re.compile('<.*?>')
    print(len(li_list))
    for divs in li_list:
        link = divs.find('a')
        link = link['href']
        #print(link)
        if link.find("flightfitnfun") > -1:
            #print('1')
            page = requests.get(link)
            soup = BeautifulSoup(page.text, "html.parser")
            detail = soup.findAll('script', {'type': 'application/ld+json'})
            detail = str(detail[1])
            start = detail.find('"name"')
            start = detail.find(":", start) + 2
            end = detail.find('"', start)
            title = detail[start:end]
            start = detail.find('"streetAddress"', end)
            start = detail.find(":", start) + 2
            end = detail.find('"', start)
            street = detail[start:end]
            start = detail.find('"addressLocality"', end)
            start = detail.find(":", start) + 2
            end = detail.find('"', start)
            city = detail[start:end]
            start = detail.find('"addressRegion"', end)
            start = detail.find(":", start) + 2
            end = detail.find('"', start)
            state = detail[start:end]
            start = detail.find('"postalCode"', end)
            start = detail.find(":", start) + 2
            end = detail.find('"', start)
            pcode = detail[start:end]
            start = detail.find('"telephone"', end)
            if start > -1:
                start = detail.find(":", start) + 2
                end = detail.find('"', start)
                phone = detail[start:end]
            else:
                phone = '<MISSING>'
            start = detail.find('"openingHours"', end)
            start = detail.find(":", start) + 2
            end = detail.find('"', start)
            hours = detail[start:end]
            hours = hours.replace(",", "|")
            soup = str(soup)
            start = soup.find('businessId')
            if start == -1:
                store = '<MISSING>'
            else:
                start = soup.find(':',start) + 3
                end = soup.find("'",start)
                store = soup[start:end]
            if len(pcode) == 4:
                pcode = '0' + str(pcode)
            lat = "<MISSING>"
            longt = "<MISSING>"
            
           


        else:
            #print('2')
            link1 = link + "directions/"
            page = requests.get(link1)
            soup = BeautifulSoup(page.text, "html.parser")
            detail = soup.findAll('iframe')
            maplink = detail[1]['src']
            #print(maplink)
            start = maplink.find("!2d")
            if start == -1:
                lat = "<MISSING>"
                longt = "<MISSING>"
            else:
                start = start + 3
                end = maplink.find("!3d", start)
                longt = maplink[start:end]
                start = end + 3
                end = maplink.find("!", start)
                lat = maplink[start:end]

            detail = soup.find('div',{'class', 'col-lg-3 footer-menu'})
            detail = detail.findAll('p')
            street = detail[0].text
            state = detail[1].text
            start = state.find(",")
            city = state[0:start]
            start = start + 2
            temp = state[start:start+3]
            start = start+3
            pcode = state[start:len(state)]

            state = temp

            phone = detail[2].text

            title = soup.find('title')
            title = title.text
            start = title.find("-")
            title = title[0:start -1]

            link1 = link + "hours-pricing/"

            page = requests.get(link1)
            soup = BeautifulSoup(page.text, "html.parser")
            detail = soup.find('table',{'class': 'table'})

            detail = detail.findAll('tr')
           
            hours = ""
            for rows in detail:
                rows = rows.text
                rows = rows.replace("\n", "")
                hours = hours + "|" + rows

            start = hours.find("Monday")
            hours = hours[start:len(hours)]
            store = "<MISSING>"
            
            

        if title.find('Sandhill') > -1:
                hours = 'MON - SUN : 9 AM - 11 PM'
        data.append([
            url,
            link,
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
            hours
        ])
        #print(p,data[p])
        p += 1
        #print('..................')
        
    return data


def scrape():
        data = fetch_data()
        write_output(data)

scrape()
