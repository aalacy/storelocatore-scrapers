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
    url = 'http://saharapizza.com/store_locations.htm'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    soup = soup.find('table',{'id': 'table2'})
    repo_list = soup.findAll('tr')
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile('<.*?>')
    phoner = re.compile('(.*?)')
    p = 1
    for repo in repo_list:
        detail = repo.findAll('td')
        if len(detail) > 1:
            td1 = detail[0]

            address = td1['title']
            address = str(address)
            address = re.sub(cleanr,"",address)

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

            title = str(td1)
            title = re.sub(pattern, "", title)
            title = re.sub(cleanr, "", title)
            title = re.sub("\n", "", title)
            start = title.find("(")
            if start != -1:
                title = title[0:start]
            start = title.find("/")
            if start != -1:
                title = title[0:start]

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



            td3 = detail[2]
            phone = td3.find('b')
            phone = str(td3)
            #start = phone.find("<",3)
            #phone = phone[0:start]
            if phone.find("#C") > -1:
                td3 = detail[3]
                phone = str(td3)

            phone = re.sub("\n", "", phone)

            phone = re.sub("\t", "", phone)
            phone = re.sub(cleanr, "", phone)
            phone = re.sub(pattern, "", phone)
            if len(phone) < 5:
                phone = "<MISSING>"
            if phone.find("ORDER") > -1:
                phone = phone[0:phone.find("ORDER")]
            if len(phone) > 15:
                phone = phone[0:15]
            if title.find("Delivery") > -1:
                title = title[0:title.find("Delivery")]
            if title.find("Download") > -1:
                title = title[0:title.find("Download")]
            if title.find("ocal") > -1:
                title = title[0:title.find("ocal")-1]

            print("<<<<<<<<<<<<<<<<<<<<<")
            temp = detail[1].text
            temp = re.sub(pattern, "", temp)
            start = temp.find("\n")
            if start > -1:
                temp = temp[0:start]
                temp = temp.rstrip()
                street = street.rstrip()
                street = street.lstrip()
            if len(temp) > 3 and street != temp:
                street = temp
                xip = "<MISSING>"
                city = title

            print(temp)
            print("<<<<<<<<<<<<<<<<<<<<<")
            print(p)
            print(title)
            print(street)
            print(city)
            print(state)
            print(xip)
            print(phone)
            print(hours)
            print("..................")
            p += 1
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
