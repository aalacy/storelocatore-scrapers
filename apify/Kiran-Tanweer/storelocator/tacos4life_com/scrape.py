from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser


logger = SgLogSetup().get_logger("tacos4life_com")

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
    search_url = "https://tacos4life.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locations = soup.find("ul", {"class": "sub-menu"}).findAll("a")
    title = soup.find("ul", {"class": "sub-menu"}).findAll("li")

    for loc, name in zip(locations, title):
        link = loc["href"]
        stores_req = session.get(link, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        title = name.text
        address = soup.find("div", {"class": "location_address"}).text
        address = address.split("\n")
        address.pop(0)
        address.pop(-1)
        if address[0] == "":
            address.pop(0)
        if address[-1] == "":
            address.pop(-1)
        if len(address) > 2:
            phone = address[-1]
            address = address[-3] + " " + address[-2]
        else:
            phone = soup.find("div", {"class": "location_phone"}).text.strip()
            address = address[0] + " " + address[1]
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
        hours = soup.find("div", {"class": "store_hours"}).text
        hours = hours.replace("\n", " ").strip()
        hours = hours.replace("ORDER ONLINE!", "").strip()
        hours = hours.replace("ORDER ONLINE", "").strip()
        hours = hours.replace("ORDER NOW", "").strip()
        hours = hours.lower()

        data.append(
            [
                "https://tacos4life.com/",
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
                "<INACCESSIBLE>",
                "<INACCESSIBLE>",
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
