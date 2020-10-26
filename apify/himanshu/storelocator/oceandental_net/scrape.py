import csv
from bs4 import BeautifulSoup as bs
import re
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('oceandental_net')


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://oceandental.net/"

    addresses = []
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}

    soup = bs(session.get("https://oceandental.net/", headers=header).text,'lxml')
    for q in soup.find("li",{"id":"menu-item-113"}).find_all("li"):
        try:
            url = (q.find("a")['href'].replace("/locations/",'https://oceandental.net/locations/'))
        except:
            continue
        page_url = ''
        soup1 = bs(session.get(url, headers=header).text,'lxml')
        latitude=''
        longitude=''
        try:
            td = soup1.find_all("a",{"style":re.compile("color:DodgerBlue;")})[-1]
            for h in soup1.find_all("a",{"style":re.compile("color:DodgerBlue;")}):
                page_url =  "https://oceandental.net"+h['href']
                soup2 = bs(session.get("https://oceandental.net"+h['href'], headers=header).text,'lxml')
                location_name = (" ".join(list(soup2.find("h1",{"class":"entry-title"}).stripped_strings)))
                addr = list(soup2.find("div",{"class":"header_contact"}).stripped_strings)
                street_address = list(soup2.find("div",{"class":"header_contact"}).stripped_strings)[0]
                city = list(soup2.find("div",{"class":"header_contact"}).stripped_strings)[1].split(",")[0]
                state = list(soup2.find("div",{"class":"header_contact"}).stripped_strings)[1].split(",")[1].strip().split()[0]
                zipcode = list(soup2.find("div",{"class":"header_contact"}).stripped_strings)[1].split(",")[1].strip().split()[1]
                phone = list(soup2.find("div",{"class":"header_contact"}).stripped_strings)[2]
                latitude =  soup2.find("iframe",{"src":re.compile("https://www.google.com")})['src'].split("!2d")[-1].split("!3d")[1].split("!2m")[0]
                longitude = soup2.find("iframe",{"src":re.compile("https://www.google.com")})['src'].split("!2d")[-1].split("!3d")[0]
                for index,dt in enumerate(addr):
                    if addr[index]=="Hours of Operation":
                        hours_of_operation = addr[index+1]

        except:
            page_url = url
            addr = list(soup1.find("div",{"class":"header_contact"}).stripped_strings)
            location_name = (" ".join(list(soup1.find("h1",{"class":"entry-title"}).stripped_strings)))
            street_address = list(soup1.find("div",{"class":"header_contact"}).stripped_strings)[0]
            city = list(soup1.find("div",{"class":"header_contact"}).stripped_strings)[1].split(",")[0]
            state = list(soup1.find("div",{"class":"header_contact"}).stripped_strings)[1].split(",")[1].strip().split()[0]
            zipcode = list(soup1.find("div",{"class":"header_contact"}).stripped_strings)[1].split(",")[1].strip().split()[1]
            phone = list(soup1.find("div",{"class":"header_contact"}).stripped_strings)[2]
            latitude =  soup1.find("iframe",{"src":re.compile("https://www.google.com")})['src'].split("!2d")[-1].split("!3d")[1].split("!2m")[0]
            longitude = soup1.find("iframe",{"src":re.compile("https://www.google.com")})['src'].split("!2d")[-1].split("!3d")[0]
            for index,dt in enumerate(addr):
                if addr[index]=="Hours of Operation":
                    hours_of_operation = addr[index+1]

        store = []
        store.append("https://oceandental.net")
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipcode if zipcode else '<MISSING>')
        store.append("US")
        store.append( '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        # logger.info("===", str(store))
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield  store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()    
