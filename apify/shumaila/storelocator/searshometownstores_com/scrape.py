import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('searshometownstores_com')





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
    cleanr = re.compile('<.*?>')
    url = 'http://www.searshometownstores.com/store-list'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    statelinks = soup.findAll('a',{'class':'primary'})
    for state in statelinks:
        state = "http://www.searshometownstores.com" + state['href']
        page1 = requests.get(state)
        soup1 = BeautifulSoup(page1.text, "html.parser")
        #maindiv = soup1.find('div', {'class': 'col-xs-12'})
        branchlink = soup1.findAll('div', {'class': 'store-list-divider'})
        #logger.info("state= ",state)
        #logger.info(len(branchlink))
        for branch in branchlink:
            link = branch.find('a')
            link = link['href']
            #logger.info("link = ",link)
            title = branch.find('strong').text
            start = len(link) - 1
            while True:
                check = link[start]
                if check == "/":
                    start = start + 1
                    store = link[start:len(link)]
                    break
                else:
                    start = start - 1
            street = branch.find('div',{'class':'text-nowrap'}).text
            #logger.info(branch.text)

            hoursd = branch.find('a',{'data-original-title':'Store Hours'})
            hoursd = hoursd['data-content']
            hours = re.sub(cleanr," ",hoursd)
            hours = hours.replace("  ", " ")
            hours = hours.lstrip()
            #logger.info(hoursd)
            city,state = title.split(",")
            state = state.lstrip()
            branchtext = branch.text
            start = branchtext.find(city) +1
            start = branchtext.find(city, start) + 1
            start = branchtext.find(state, start) + 1
            start = branchtext.find(" ", start)
            temp = branchtext[start:len(branchtext)]
            temp = temp.lstrip()
            start = temp.find("Phone")
            if start != -1:
                pcode = temp[0:start]
                start = temp.find(" ", start)
                end = temp.find("Hours")
                phone = temp[start:end]
                phone = phone.strip()
            else:
                phone = "<MISSING>"


            pcode = pcode.strip()

            #logger.info(title)
            #logger.info(store)
            #logger.info(street)
            #logger.info(city)
            #logger.info(state)
            #logger.info(pcode)
            #logger.info(phone)
            #logger.info(hours)
            if len(phone)<3:
                phone = "<MISSING>"
            if len(hours)< 3:
                hours = "<MISSING>"
            if len(pcode) <5:
                pcode = "0" + pcode

            data.append([
                'http://www.searshometownstores.com/',
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
                "<MISSING>",
                "<MISSING>",
                hours
            ])



    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()

