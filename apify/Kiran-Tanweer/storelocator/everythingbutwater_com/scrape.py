from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser


session = SgRequests()
website = "everythingbutwater_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.everythingbutwater_com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://www.everythingbutwater.com/company/stores"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        loc_block = soup.find("section", {"id": "stores-content"}).findAll(
            "div", {"class": "row"}
        )
        for loc in loc_block:
            try:
                title = loc.find("p", {"class": "location-name"}).text
                address = loc.find("a", {"class": "directions"})["href"]
                address = address.split("q=")[1]
                address = address.replace("+", " ")
                phone_hours = loc.findAll("p", {"class": "phone-hours"})
                phone = phone_hours[0].text.strip()
                hours = phone_hours[1].text.strip()
                if hours == "":
                    hours = phone_hours[-1].text.strip()
                    if hours == "Opening soon":
                        hours = "Coming Soon"
                    else:
                        hours = "Closed Temporarily"
            except AttributeError:
                continue
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

            if street == "5":
                street = "5 Woodfield Shopping Center"

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=search_url,
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
