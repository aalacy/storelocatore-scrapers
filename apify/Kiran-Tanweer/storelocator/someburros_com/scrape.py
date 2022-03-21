from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser


session = SgRequests()
website = "someburros_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.someburros.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://someburros.com/locations/"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        loc_block = soup.find("article", {"id": "post-9"}).findAll("div")
        for i in range(0, len(loc_block) - 5):
            if i % 5 == 0:
                location = loc_block[i]
                title = location.find("h3").text
                address = location.find("p").text
                address = address.split("\n")
                try:
                    address = address[0] + " " + address[1]
                    ptags = location.findAll("p")
                    hours = ptags[-1].text
                    hours = hours.replace("\n", " ")
                    hours = hours.replace("7 days a week", "Mon-Sun")
                    hours = hours.replace(
                        "Open every home game at Sun Devil Stadium!", "<MISSING>"
                    )
                    phone = ptags[0].text
                    phone = phone.split("\n")[-1]
                    if phone.find("-") == -1:
                        phone = "<MISSING>"
                    parsed = parser.parse_address_usa(address)
                    street1 = (
                        parsed.street_address_1
                        if parsed.street_address_1
                        else "<MISSING>"
                    )
                    street = (
                        (street1 + ", " + parsed.street_address_2)
                        if parsed.street_address_2
                        else street1
                    )
                    city = parsed.city if parsed.city else "<MISSING>"
                    state = parsed.state if parsed.state else "<MISSING>"
                    pcode = parsed.postcode if parsed.postcode else "<MISSING>"
                    hours = hours.replace("â€“", "-").strip()
                    title = title.replace("â€“", "-").strip()
                    phone = phone.split("â€¬")[0]

                except IndexError:
                    title = title + " " + "Coming Soon"
                    hours = MISSING
                    street = MISSING
                    city = MISSING
                    state = MISSING
                    pcode = MISSING
                    phone = MISSING

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url="https://someburros.com/locations/",
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
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
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME})
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
