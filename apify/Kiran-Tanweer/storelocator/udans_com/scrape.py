from bs4 import BeautifulSoup
import csv
import re
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser

logger = SgLogSetup().get_logger("udans_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    search_url = "https://udans.com/pages/ud-locations"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locations = soup.findAll("div", {"class": "store-info-floating-box"})
    for loc in locations:
        title = loc.find("h3").text.strip()
        address = loc.findAll("p")[1]
        phone = loc.find("span", {"itemprop": "telephone"}).text
        hours = loc.find("div", {"class": "regular-hours"}).text
        hours = re.sub(pattern, " ", hours)
        hours = re.sub(cleanr, " ", hours)
        hours = hours.split("Regular Hours: ")[1]
        address = str(address)
        address = address.replace("\n", "")
        address = address.lstrip("<p>")
        address = address.rstrip("</p>")
        address = address.replace("<br>", " ")
        address = address.replace("</br>", " ")
        address = address.replace("<br/>", " ")
        address = address.replace("</br", " ")
        address = address.strip()
        parsed = parser.parse_address_usa(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"

        if street == "599 W Glen Bay Ave":
            street = "599 W Glen Bay Ave Bayshore Town Center"
            city = "Glendale"
        data.append(
            [
                "https://udans.com/",
                search_url,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
