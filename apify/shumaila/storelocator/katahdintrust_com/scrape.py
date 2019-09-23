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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    url = 'https://www.katahdintrust.com/Locations-Hours'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    # print(soup)
    title_list = soup.findAll('table', {'class': 'Subsection-Table'})
    repo_list = soup.findAll('table', {'class': 'Table-Location'})
    p = 1
    flag = False
    for repo in repo_list:
        det = repo.findAll('p')
        if p == 3:
            if flag:
                title = title_list[p].find('h3').text
                p += 1

            else:
                img = det[0].find('img')
                title = img['alt']
                title = title.replace("Location ","")
                flag = True
        else:

            title = title_list[p].find('h3').text
            p += 1






        address = det[1].text
        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        j = 2
        hours = ""
        phone = ""
        ltype = ""
        while j < len(det):
            if det[j].text.find("am") > -1:
                hours = hours + " | " + det[j].text
            if det[j].text.find("(") > -1:
                phone = phone + " | " + det[j].text
            if det[j].text.find("ATM") > -1:
                ltype = det[j].text
            j += 1

        phone = phone[2:len(phone)]
        hours = hours[2:len(hours)]
        if len(hours) < 3:
            start = ltype.find("ATM")
            hours = ltype[0:4]

        if len(ltype) < 3:
            ltype = "<MISSING>"
        else:
            ltype = ltype[5:len(ltype)]
        if len(phone) < 3:
            phone = "<MISSING>"
        if len(hours) < 3:
            hours = "<MISSING>"
        if phone.find("Phone") != -1 or phone.find("(Toll Free)") != -1:
            phone = phone.replace("Phone:", "")
            phone = phone.replace("Phone :", "")
            phone = phone.replace("(Toll Free)", "")
        hours = hours.replace(",", "-")
        phone = phone.lstrip()
        street = street.lstrip()
        street = street.replace(",","")
        city = city.replace(",","")
        city = city.lstrip()
        state = state.lstrip()
        pcode = pcode.lstrip()
        hours = hours.lstrip()
        start = phone.find("|")
        if start != -1:
            phone = phone[start+2:len(phone)]
        print(title)
        print(street)
        print(city)
        print(state)
        print(pcode)
        print(ltype)
        print(phone)
        print(hours)
        print(p)
        print(".................")
        data.append([
            url,
            title,
            street,
            city,
            state,
            pcode,
            "US",
            "<MISSING>",
            phone,
            ltype,
            "<MISSING>",
            "<MISSING>",
            hours
        ])

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()