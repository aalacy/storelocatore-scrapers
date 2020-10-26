import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
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
    links = []
    cleanr = re.compile('<.*?>')
    url = 'http://pizzafusion.com/locations/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    maindiv = soup.find('div', {'id': 'usa3'})
    divs = maindiv.findAll('div')
    print("ENTER")
    n = 2
    for div in divs:
        dets = div.findAll('div')
        for linka in dets:
            try:
                link = linka.find('a',{'class': 'borderImg'})
                link = link["href"]
                link = str(link)
                if link.find("#") == -1:
                    links.append("http://pizzafusion.com" + link)

            except:
                flag = 2


    for n in range(0, len(links)):
        link = links[n]
        try:
            page = requests.get(link)
            #print(page)
            print(link)
            soup = BeautifulSoup(page.text, "html.parser")
            td = soup.find("td")
            td = str(td)
            td = re.sub(cleanr, " ", td)

            td = td.replace("\n", "|")
            td = td.replace("\r", "|")
            td = td.replace("||", "|")
        except:
            print(link)
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            maindiv = soup.find('div', {'id': '117'})
            divs = maindiv.find('div')
            td = divs.find('p')
            td = str(td)
            td = re.sub(cleanr, " ", td)
            td = td.replace("  ", "|")
            flag = 1
        try:
            mainframe = soup.findAll('iframe')
                #print(mainframe[1])
            maplink = str(mainframe[1])
            start = maplink.find("sll") +5
            start = maplink.find("ll",start)+3
            end = maplink.find(",", start)
            lat = maplink[start:end]
            start = end + 1
            end = maplink.find("&", start)
            longt = maplink[start:end]
        except:
            lat = "<MISSING>"
            longt = "<MISSING>"


            # print(maplink)
        p = n + 1

        print(td)
        if flag == 1:
            start = td.find("|", 3)
            title = td[1:start]
        else:
            start = td.find(",", 0)
            title = td[2:start]
        if td.find("#") > -1:
            start = td.find("#")
            end = td.find("|", start)
            store = td[start + 1:end]
        else:
            store = "<MISSING>"

        end = td.find("Phone")


        address = td[start:end]

        if flag == 1:
            address = address.replace("|", " ")

        address = usaddress.parse(address)
        #print(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""

        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                    temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1 or temp[1].find("LandmarkName") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]

            i += 1

        start = td.find(":", start) + 1
        end = td.find("Hours", start)
        phone = td[start:end]
        if phone.find("Fax"):
            phone = phone[0:phone.find("Fax")]
        start = td.find("Hours")
        start = td.find(":",start) + 2
        hours = td[start:len(td)]
        start = hours.find("[")
        if start != -1:
            hours = hours[0:start-1]

        phone = phone.replace("\n","")
        phone = phone.replace("|", "")
        title = title.lstrip()
        street = street.lstrip()
        city =city.lstrip()
        city = city.replace(",", "")
        pcode = pcode.lstrip()
        state = state.lstrip()
        phone = phone.lstrip()
        hours = hours.replace("|","")
        hours = hours.replace(" &amp; ", "-")
        hours = hours.lstrip()
        hours = hours.replace("\n", "")
        pcode = pcode.replace("|","")

        store = store.lstrip()
        flag =0
        print(p)
        print(store)
        print(title)
        print(street)
        print(city)
        print(state)
        print(pcode)

        print(phone)
        print(hours)
        print(lat)
        print(longt)
        print("...................................")
        data.append([
            url,
            title,
            street,
            city,
            state,
            pcode,
            'US',
            store,
            phone,
            '<MISSING>',
            lat,
            longt,
            hours
        ])


    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
