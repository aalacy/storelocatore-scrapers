# Import libraries
import xml
import lxml
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
    url = 'http://saharapizza.com/store_locations.htm'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    soup = soup.find('table',{'id': 'table2'})
    repo_list = soup.findAll('tr')


    cleanr = re.compile('<.*?>')
    phoner = re.compile('(.*?)')
    for repo in repo_list:
        detail = repo.findAll('td')
        if len(detail) == 3:
            td1 = detail[0]
            address = td1['title']
            address = str(address)
            address = re.sub(cleanr,"",address)
            print(address)
            start = address.find(",")
            street = address[0:start]
            midn = address.find(",", start+2)
            city = address[start+2:midn]
            state = address[midn+2:len(address)]
            start = state.find(" ")
            if start == -1 or state.find("Sante") > -1:
                xip = "<MISSING>"
            else:
                xip = state[start+1:len(state)]
                state = state[0:start]
            print(street)
            print(city)
            print(state)
            print(xip)
            title = td1.find('b')
            title = str(title)
            start = title.find("<br")
            if start != -1:
                title = title[0:start]
            title = re.sub(cleanr,"",title)
            title = re.sub("\r\n", " ", title)
            title = re.sub("\t", "", title)
            print(title)
            td2 = detail[1]
            temp = str(td2)
            start = temp.find("Hours")
            if start != -1:
                hours = temp[start+6:len(temp)]
                hours = re.sub(cleanr, "", hours)
                hours = re.sub("\r\n", " ", hours)
                hours = re.sub("\t", "", hours)
                hours = hours[2:len(hours)]
            else:
                hours = "<MISSING>"

            print(hours)

            td3 = detail[2]
            phone = td3.find('b')
            phone = str(phone)
            start = phone.find("<",3)
            phone = phone[0:start]
            phone = re.sub("\r", " ", phone)
            phone = re.sub("\t", "", phone)
            phone = re.sub(cleanr, "", phone)
            phone = re.sub(" ", "-", phone)
            if phone.find("(") > -1:
                start = phone.find("-")
                phstr = phone[1:start-1]
                phone = phstr + phone[start:len(phone)]

            if phone == "Non":
                phone = "<MISSING>"

            print(phone)

            print("..................")
            if title.find("Bolivia") == -1:
                data.append([
                    url,
                    title,
                    street,
                    city,
                    state,
                    xip,
                    'US',
                    '<MISSING>',
                    phone,
                    '<MISSING>',
                    '<MISSING>',
                    '<MISSING>',
                    hours
                ])

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
