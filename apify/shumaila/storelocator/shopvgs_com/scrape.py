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
    #shopvgs.com
    url = 'https://www.shopvgs.com/locations'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    #print(soup)
    repo_list = soup.findAll('div',{'class':'store'})

    soup = str(soup)
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    for repo in repo_list:
        link = repo.find('a')
        title = link.text
        try:
            lat = repo['data-latitude']
        except:
            lat = "<MISSING>"
        try:
            longt = repo['data-longitude']
        except:
            longt = "<MISSING>"

        link = link['href']
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        try:
            address = soup.find('address').text
            address = re.sub(pattern," ",address)
            address = address.lstrip()
            address = usaddress.parse(address)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                        temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                    "USPSBoxID") != -1:
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1

            street = street.lstrip()
            city = city.lstrip()
            state = state.lstrip()
            pcode = pcode.lstrip()
            city = city.replace(",", "")

        except:
            street = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            pcode = "<MISSING>"
        try:
            phone = soup.find('div',{'class':'contact text-center'}).text
            phone = re.sub(pattern, "", phone)
            phone = phone.replace("\n","|")
            phone = phone.lstrip()
            start = phone.find("(")
            end = phone.find("|",start)
            phone = phone[start:end]
        except:
            phone = "<MISSING>"
        try:
            hours = soup.find('table',{'class':'table table-striped responsive hours'}).text
            hours = re.sub(pattern,"",hours)
            hours = hours.replace("\n"," | ")
            hours = hours.lstrip()
        except:
            hours = "<MISSING>"

        try:
            ltype = soup.find('div',{'class':'departments'}).text
            ltype = re.sub("\n","|",ltype)
            ltype = ltype.replace("|||","|")
            ltype = ltype[1:len(ltype)-1]
        except:
            ltype = "<MISSING>"



        #print(address)
        #print(link)
        #print(title)
        #print(street)
        #print(city)
        #print(state)
        #print(pcode)
        #print(phone)
        #print(hours)
        #print(ltype)
        #print(lat)
        #print(longt)
        #print("....................")
        data.append([
            'https://www.shopvgs.com/',
            link,
            title,
            street,
            city,
            state,
            pcode,
            'US',
            "<MISSING>",
            phone,
            ltype,
            lat,
            longt,
            hours
        ])



    return data


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
