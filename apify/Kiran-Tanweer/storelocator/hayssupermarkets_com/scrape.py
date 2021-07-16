from bs4 import BeautifulSoup
import csv
import time
import re
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser

logger = SgLogSetup().get_logger("hayssupermarkets_com")

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
    search_url = "https://www.hayssupermarkets.com/my-store/store-locator"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locations = soup.findAll("ul", {"class": "sub-menu"})[2].findAll("a")
    for link in locations:
        link = "https://www.hayssupermarkets.com" + link["href"]
        if link.find("store-locator") == -1:
            stores_req = session.get(link, headers=headers)
            soup = BeautifulSoup(stores_req.text, "html.parser")
            title = soup.find("span", {"class": "store-name"}).text
            address = soup.find("div", {"class": "fp-store-address"}).text
            address = address.split(title)[1].strip()
            address = re.sub(pattern, " ", address)
            address = re.sub(cleanr, " ", address)
            parsed = parser.parse_address_usa(address)
            street1 = (
                parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
            )
            street = (
                (street1 + ", " + parsed.street_address_2)
                if parsed.street_address_2
                else street1
            )
            city = parsed.city if parsed.city else "<MISSING>"
            state = parsed.state if parsed.state else "<MISSING>"
            pcode = parsed.postcode if parsed.postcode else "<MISSING>"
            hours = soup.find("div", {"class": "col-md-4"}).findAll("p")[0].text
            phone = soup.find("div", {"class": "col-md-4"}).findAll("p")[1].text
            phone = phone.split("Fax")[0].strip()

            coords = str(soup)
            lat = coords.split('"latitude":')[1].split(',"')[0]
            lng = coords.split('"longitude":')[1].split("}")[0]

            data.append(
                [
                    "https://www.hayssupermarkets.com",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    lat,
                    lng,
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
