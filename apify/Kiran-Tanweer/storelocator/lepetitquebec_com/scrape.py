import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
import time
import re
from sgscrape import sgpostal as parser

logger = SgLogSetup().get_logger("lepetitquebec_com")

session = SgRequests()

headers = {
    "authority": "lepetitquebec.com",
    "method": "GET",
    "path": "/fr/restaurants/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "identity",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "__cfduid=d61e5e00408ebaf9e2f6a557dce8ad3f31618316909; django_language=fr; __utmc=193871408; __utmz=193871408.1618316913.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); sessionid=9bfc0993ac071f3b80b594f67d940456; csrftoken=c8d032dae768e60fae29e5c1349fccae; __utma=193871408.1248379655.1618316913.1618316913.1618428563.2; __utmt=1; __utmb=193871408.3.10.1618428563",
    "referer": "https://lepetitquebec.com/fr/franchises/",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    search_url = "https://lepetitquebec.com/fr/restaurants/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    divlist = soup.findAll("div", {"class": "cols"})
    soup = str(soup)
    coords = soup.split("var LatLngList = [];")[1].split("];")[0]
    coords = coords.lstrip("var LatLngList = [")
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    coords = re.sub(pattern, " ", coords)
    coords = re.sub(cleanr, " ", coords)
    coords = coords.split("new google.maps.LatLng(")
    coords.pop(0)
    for div, coord in zip(divlist, coords):
        latlng = coord.rstrip(")")
        latlng = latlng.split(",")
        lat = latlng[0].strip()
        lng = latlng[1].rstrip(")")
        lng = lng.replace(")", "").strip()
        title = div.find("h2").text
        address = div.find("p")
        address = str(address)
        address = address.replace("<p>", "")
        address = address.replace("</p>", "")
        address = address.replace("\n", "")
        address = address.replace("<br/>", " ")
        address = address.strip()
        phone = address.split(" ")[-1].strip()
        address = address.split(phone)[0]
        address = address.strip()

        parsed = parser.parse_address_intl(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"
        country = "CAN"

        data.append(
            [
                "https://lepetitquebec.com/",
                "https://lepetitquebec.com/fr/restaurants/",
                title,
                street,
                city,
                state,
                pcode,
                country,
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                lng,
                "<MISSING>",
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
