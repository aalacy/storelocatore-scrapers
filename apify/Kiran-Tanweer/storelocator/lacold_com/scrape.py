from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser

logger = SgLogSetup().get_logger("lacold_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
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
    search_url = "https://www.lacold.com/facilities/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locations = soup.findAll("a", {"class": "page-media"})
    for loc in locations:
        link = loc["href"]
        title = link.split("facilities/")[1]
        title = title.replace("-", " ")
        title = title.replace("facility", "warehouse")
        title = title.replace("/", "").strip()
        locs = []
        stores_req = session.get(link, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        location = soup.findAll("div", {"class": "wpb_wrapper"})
        if link == "https://www.lacold.com/facilities/main-office/":
            locs.append(location[-1])
            locs.append(location[-5])
        else:
            locs.append(location[-1])
            locs.append(location[-2])
        for loc in locs:
            details = loc.findAll("p")
            address = details[0].text.strip()
            address = address.replace("\n", " ")
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
            contact = details[1].text
            phone = contact.replace("\n", "")
            phone = phone.split("Fax")[0]
            phone = phone.split("Tel:")[1].strip()
            hours = contact.replace("\n", " ")
            hours = hours.split("Hours")[1]
            hours = hours.lstrip(":").strip()
            hours = hours.replace("of Operation: ", "").strip()
            hours = hours.replace("Office:", "").strip()
            hours = hours.replace("Warehouse:", "").strip()
            hours = hours.replace("  ", " ").strip()

            if street != "715 E Fourth St":

                data.append(
                    [
                        "https://www.lacold.com/",
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
