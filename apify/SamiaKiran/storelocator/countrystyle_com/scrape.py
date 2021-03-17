<<<<<<< Updated upstream
import csv
from sgrequests import SgRequests
from sglogging import sglog

website = "dibellas_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    final_data = []
    if True:
        url = "https://api.chepri.io/dibellas/custom/dineengine/vendor/olo/restaurants?includePrivate=false"
        loclist = session.get(url, headers=headers).json()["restaurants"]
        for loc in loclist:
            link = loc["url"]
            title = loc["storename"]
            store = loc["id"]
            street = loc["streetaddress"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["zip"]
            lat = loc["latitude"]
            longt = loc["longitude"]
            phone = loc["telephone"]
            hours = "<INACCESSIBLE>"
            final_data.append(
                [
                    "https://www.dibellas.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "USA",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours.strip(),
                ]
            )
        return final_data
=======
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape import sgpostal as parser
from bs4 import BeautifulSoup

website = "countrystyle_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.countrystyle.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1615704674870"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("store").findAll("item")
        for loc in loclist:
            location_name = loc.find("location").text
            store = loc.find("sortord").text
            raw_address = loc.find("address").text.replace(",", "")
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            street_address = (
                street_address + ", " + formatted_addr.street_address_2
                if formatted_addr.street_address_2
                else street_address
            )
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
            city = formatted_addr.city
            zip_postal = loc.find("telephone").text
            if not zip_postal:
                zip_postal = "<MISSING>"
            state = loc.find("country").text
            latitude = loc.find("latitude").text
            longitude = loc.find("longitude").text
            phone = loc.find("fax").text
            if not phone:
                phone = "<MISSING>"

            yield SgRecord(
                locator_domain="https://www.countrystyle.com/",
                page_url="https://www.countrystyle.com/stores/",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="CA",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation="<MISSING>",
                raw_address=raw_address,
            )
>>>>>>> Stashed changes


def scrape():
    log.info("Started")
<<<<<<< Updated upstream
    data = fetch_data()
    write_output(data)
=======
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
>>>>>>> Stashed changes
    log.info("Finished")


if __name__ == "__main__":
    scrape()
