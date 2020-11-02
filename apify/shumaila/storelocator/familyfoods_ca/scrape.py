# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('familyfoods_ca')



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
    url = 'http://familyfoods.ca/store-locator/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    nextl = soup.find('ul',{'class': 'sub-menu'})
    repo_list = nextl.findAll('li')
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    for repo in repo_list:
        link = repo.find('a')
        link = link['href']
        logger.info(link)
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        detlist = soup.findAll('div', {'class': 'location-info'})
        for detail in detlist:
           # logger.info(detail)
            address = detail.find('a')
            detail = str(detail)
            start = detail.find(">")+1
            end = detail.find("<br",start)
            title = detail[start:end]
            title = re.sub(pattern,"",title)
            #start = detail.find("Address", end) + 1
            #logger.info(start)
            try:
                href = address['href']
                href = str(href)
                start = href.find("@") + 1


                if start == 0:
                    longt = "<MISSING>"
                    lat = "<MISSING>"
                else:
                    end = href.find(",", start)
                    lat = href[start:end]
                    lat = re.sub(pattern, "", lat)

                    start = end + 1

                    end = href.find(",", start)


                    longt = href[start:end]
                    longt = re.sub(pattern, "", longt)

            except:
                lat = "<MISSING>"
                longt = "<MISSING>"

            logger.info(title)
            logger.info(lat)
            logger.info(longt)
            start = 0
            start = detail.find("Address")
            start = detail.find("blank",start)
            if start != -1:
                if title.find(" Watt Street Family Foods") == -1:

                    start = detail.find(">", start)
                    end = detail.find("</div>", start)
                    address = detail[start+1:end]
                else:
                    start = detail.find('"', start)
                    end = detail.find("</div>", start)
                    address = detail[start + 1:end]

                if address[1] == '/':
                    address = detail[start+4:end]
                # logger.info("?????????????")
                # logger.info(address)
                start = 0
                end = address.find("<br")
                if end == -1:
                    end = address.find(",")
                street = address[start:end]
                logger.info(street)
                start = address.find("r/>", end)
                # logger.info(start)
                if start == -1:
                    start = address.find(",", end)
                else:
                    start = start + 3
                end = address.find(",", start)
                if end == -1:
                    end = address.find(" ", start)
                city = address[start:end]
                if len(city) == 0:
                    city = address[start+2:end]

                if len(city) < 2:
                    start = start + 3
                    city = address[start:end]
                start = end + 1
                end = address.find(",", start+1)
                if end == -1:
                    end = address.find(" ", start + 2)

                state = address[start:end]
            # logger.info(state)
                start = end + 1
                end = address.find("<",start)
                xip = address[start:end]
            else:
                start = detail.find("indent")
                start = detail.find(">",start)
                if detail[start+2] != "a":
                    end = detail.find("<", start)
                else:
                    start = start + 4
                    start = detail.find(">")
                    end = detail.find("<", start)
                street = detail[start+1:end]
                logger.info(street)
                city = "<MISSING>"
                state = "<MISSING>"
                start = detail.find("r>", start)
                end = detail.find("<", start)
                xip = detail[start + 2:end]



            # logger.info(xip)
            start = detail.find("Phone") + 7
            end = detail.find("<br", start)
            phone = detail[start:end]
            # logger.info(phone)
            street = street.lstrip()
            city = city.lstrip()
            state = state.lstrip()
            xip = xip.lstrip()
            if lat.find("div") > -1:
                lat = "<MISSING>"
            if longt.find("div") > -1:
                longt = "<MISSING>"
            if phone.find("div") > -1:
                phone = "<MISSING>"
            if xip.find("div") > -1:
                xip = "<MISSING>"
            if phone.find("location-info") > -1:
                phone = "<MISSING>"
            if street.find("div") > -1:
                street = "<MISSING>"
            if state.find("div") > -1:
                state = "<MISSING>"

            if street.find(">") == 0:
                street = city[1:len(street)]
            if lat.find("://") != -1:
                lat = "<MISSING>"
            if longt.find("://") != -1:
                longt = "<MISSING>"
            street = re.sub(cleanr,"", street)
            state = re.sub(cleanr, "", state)

            if len(xip) > 7:
                if xip.find("Fax") == -1:
                    city = state
                    start = xip.find(" ")
                    state = xip[0:start]
                    xip = xip[start + 1:len(xip)]
                else:
                    xip = "<MISSING>"

            if state == "P0T":
                xip = state + xip
                state = "<MISSING>"
            if xip == "R2K 2S":
                xip = "R2K 2S9"
            if xip.find("R0G 1GO") != -1:
                xip = "R0G 1G0"
                logger.info(xip[1:3])
                logger.info(xip[5])

            if len(xip) < 4:
               xip = "<MISSING>"

            if len(street) < 3 or street.isspace():
                street = "<MISSING>"
            if len(city) < 3:
                city = "<MISSING>"
            if len(state) < 2:
                state = "<MISSING>"
            if len(phone) < 3:
                phone = "<MISSING>"
            if city.find(">") != -1:
                city = "<MISSING>"
            state = state.rstrip()
            if state == "<MISSING":
                state = "<MISSING>"
            if state == "NWT":
                state = "NT"

            logger.info(city)
            logger.info(state)
            logger.info(xip)
            logger.info(phone)
            logger.info("..................")

            data.append([
                url,
                title,
                street,
                city,
                state,
                xip,
                "CA",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                longt,
                "<MISSING>"
            ])

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
