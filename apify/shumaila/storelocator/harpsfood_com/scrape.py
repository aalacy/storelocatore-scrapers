import requests
from bs4 import BeautifulSoup
import csv
import usaddress
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('harpsfood_com')




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
    url = 'https://www.harpsfood.com/StoreLocator/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    repo_list = soup.findAll('ul', {'style': 'list-style: none;'})
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    for repo in repo_list:
        dets = repo.findAll('a')
        for links in dets:
            link = links['href']
            link = link.replace("..","")
            link = "https://www.harpsfood.com" + link
            logger.info(link)
            page = requests.get(link)
            soup = BeautifulSoup(page.text, "html.parser")
            detail = soup.find('table')
            trow = detail.findAll('td', {'align' : 'right'})
            for td in trow:
                link = td.find('a')
                try:
                    link = link['href']
                    logger.info(link)
                    page = requests.get(link)
                    soup = BeautifulSoup(page.text, "html.parser")
                    address = soup.find('p', {'class': 'Address'}).text
                    address = re.sub("\n", "", address)
                    state = address.find(":")
                    address = address[0: len(address)]
                    address = usaddress.parse(address)
                    i = 0
                    street = ""
                    city = ""
                    state = ""
                    pcode = ""
                    while i < len(address):
                        temp = address[i]
                        if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("LandmarkName") != -1:
                            if temp[1].find("StreetNamePostType") > -1 and temp[0].find(",") > -1:
                                city = city + " " + temp[0]
                            else:
                                street = street + " " + temp[0]
                        if temp[1].find("PlaceName") != -1:
                            city = city + " " + temp[0]
                        if temp[1].find("StateName") != -1:
                            state = state + " " + temp[0]
                        if temp[1].find("ZipCode") != -1:
                            pcode = pcode + " " + temp[0]

                        i += 1
                    logger.info(address)
                    try:
                        phone = soup.find('p', {'class': 'PhoneNumber'})
                        phone = phone.find('a').text
                    except:
                        phone = "<MISSING>"

                    title = soup.find('h3').text
                    start = title.find("#")
                    if start != -1:
                        store = title[start+1:len(title)]
                    else:
                        store = "<MISSING>"

                    dl = soup.find('dl')
                    dd = dl.findAll('dd')
                    dt = dl.findAll('dt')
                    flag = True
                    i = 0
                    hours = ""
                    try:
                        while flag:
                            if dt[i].text.find("Services") == -1:
                                hours = hours + dt[i].text + dd[i].text + " | "
                            else:
                                hours = hours[0:len(hours) - 2]
                                flag = False
                            i += 1
                    except:
                        logger.info("..")
                    # logger.info(dl)
                    city = city.replace(",", "")
                    start = street.find(":")
                    street = street[start+1:len(street)]
                    street = street.lstrip()
                    city = city.lstrip()
                    state = state.lstrip()
                    pcode = pcode.lstrip()

                    try:
                        script = str(soup)
                        start = script.find("initializeMap")
                        start = script.find("(", start)
                        end = script.find(")", start)
                        script = script[start+1:end]
                        script = script.replace('"',"")
                        lat, longt = script.split(",")
                    except:
                        lat = "<MISSING>"
                        long = "<MISSING>"


                    if len(street) < 4:
                        address = "<MISSING>"
                    if len(title) < 3:
                        title = "<MISSING>"
                    if len(city) <3:
                        city = "<MISSING>"
                    if len(state) <2:
                        state = "<MISSING>"
                    if len(pcode) < 5:
                        pcode = "<MISSING>"
                    if len(phone) < 6:
                        phone = "<MISSING>"
                    if len(lat) < 2 or lat == "undefined":
                        lat = "<MISSING>"
                    if len(longt) < 2 or longt == "undefined":
                        longt = "<MISSING>"

                    logger.info(title)
                    logger.info(street)
                    logger.info(city)
                    logger.info(state)
                    logger.info(pcode)
                    logger.info(phone)
                    logger.info(store)
                    logger.info(lat)
                    logger.info(longt)
                    logger.info(hours)
                    logger.info(p)
                    logger.info("................")

                    data.append([
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
                        hours
                    ])
                    p += 1

                except:
                    logger.info("error")

    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
