from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser


session = SgRequests()
website = "luckyssteakhouse_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://luckyssteakhouse.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        locations = []
        search_url = "https://luckyssteakhouse.com/locations/"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        loc_block = soup.findAll("a", {"class": "pattern"})
        for loc in loc_block:
            url = loc["href"]
            if url == "https://luckyssteakhouse.com/locations/luckys-steakhouse/":
                stores_req = session.get(url, headers=headers)
                soup = BeautifulSoup(stores_req.text, "html.parser")
                loc_block = soup.find("div", {"class": "locations-list"}).findAll(
                    "a", {"class": "button"}
                )
                for loc in loc_block:
                    locations.append(loc["href"])
            else:
                locations.append(url)

        for loc in locations:
            stores_req = session.get(loc, headers=headers)
            soup = BeautifulSoup(stores_req.text, "html.parser")
            title = (
                loc.split("locations/")[1].replace("/", " ").replace("-", " ").strip()
            )
            phone = soup.findAll("h2")
            if len(phone) >= 2:
                phone = phone[1].text
            else:
                phone = phone[0].text
            address = soup.find("h3", {"class": "pattern"}).text

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

            hours = soup.find("div", {"class": "menu-hours"}).text
            hours = (
                hours.replace("\n", " ")
                .replace("Our MenuRestaurant Hours", "")
                .replace("“*Now Accepting reservations, call to inquire**", "")
                .strip()
            )

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://someburros.com/locations/",
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="US",
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
